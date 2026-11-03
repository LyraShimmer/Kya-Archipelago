"""Opt-in Kya AutoSave (PCSX2 PINE) -- NO normal savestate slots touched.

PCSX2 PINE 0x09 accepts a byte slot, and PCSX2 VMManager uses that slot
number verbatim in filename. We exclusively use high-numbered 200..205,
never the user-visible 0..9. The game RAM is read-only here.

This first version refuses unknown existing high-slot files; it does not
silently replace anything that it didn't itself create/confirm.
"""
from __future__ import annotations

import json
import math
import os
import struct
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

AUTOSAVE_SLOTS = (200, 201, 202, 203, 204, 205)
INTERVAL_SECONDS = 120.0
SAMPLE_PERIOD = 2.5
ZONE_SETTLE_SECONDS = 15.0
STREAM_SETTLE_SECONDS = 15.0
MIN_STILL_SECONDS = 4.0
RECENT_MOVEMENT_SECONDS = 35.0
MIN_SAVE_GAP_SECONDS = 20.0
VERIFICATION_TIMEOUT_SECONDS = 45.0
ACTOR_ADDR = 0x00448E10
PLAYER_ADDR = 0x006F3D90
VALID_GAME_ID = "SLES51473"


def _ptr_ok(ptr: int) -> bool:
    return 0x01000000 <= ptr < 0x02000000 and ptr % 4 == 0


def _float32(value: int) -> float:
    return struct.unpack('<f', struct.pack('<I', value & 0xFFFFFFFF))[0]


def _belongs_to_kya(path: Path) -> bool:
    return 'SLES51473' in ''.join(x for x in path.name.upper() if x.isalnum())


def default_sstates_path() -> Path:
    home = Path(os.environ.get('USERPROFILE', str(Path.home())))
    return home / 'Documents' / 'PCSX2' / 'sstates'


@dataclass(frozen=True)
class Frame:
    stamp: float
    zone: str
    generation: tuple[int, int]
    actor: int
    state: int
    position: tuple[float, float, float]


class AutoSaveController:
    """Called exclusively on the launcher's existing PINE owner thread."""

    def __init__(self, logger, path: Path | None = None, clock=time.monotonic):
        self.log = logger
        self.path = Path(path) if path is not None else default_sstates_path()
        self.clock = clock
        self.enabled = False
        self.session_tag = uuid.uuid4().hex
        self.ap_identity = ''
        self.pending_identity = ''
        self.language = 'en'
        self.next_slot = 0
        self.last_request_at = -float('inf')
        self.next_periodic_at = 0.0
        self.previous: Frame | None = None
        self.zone_since = 0.0
        self.generation_since = 0.0
        self.still_since = 0.0
        self.moved_at = -float('inf')
        self.move_states: dict[int, float] = {}
        self.pending_zone_save = False
        self.pending_verification: tuple[int, float, dict[str, tuple[int, int]]] | None = None
        self.next_sample_at = 0.0
        self.last_skip_note = ''
        self.last_skip_at = 0.0

    def _files_in_slot(self, slot: int) -> list[Path]:
        # Standard PCSX2 naming: SERIAL (CRC).200.p2s.
        return [f for f in self.path.glob(f'*.{slot}.p2s') if f.is_file() and _belongs_to_kya(f)]

    def _marker(self, slot: int) -> Path:
        return self.path / f'Kya_Archipelago_AutoSave_Slot_{slot}.json'

    def _preflight(self) -> None:
        if not self.path.is_dir():
            raise RuntimeError(f"Dossier savestates introuvable: {self.path}")
        for slot in AUTOSAVE_SLOTS:
            files = self._files_in_slot(slot)
            mark = self._marker(slot)
            backup_files = [f for f in self.path.glob(f'*.{slot}.p2s.backup')
                            if f.is_file() and _belongs_to_kya(f)]
            if backup_files and not mark.exists():
                raise RuntimeError(f"Slot interne {slot} a un backup inconnu: {backup_files[0].name}. Aucun écrasement.")
            if len(files) > 1:
                raise RuntimeError(f"Plusieurs savestates Kya utilisent le slot {slot}; AutoSave refusé.")
            if files:
                if not mark.exists():
                    raise RuntimeError(f"Slot interne {slot} déjà occupé sans marque AutoSave: {files[0].name}. Aucun écrasement.")
                try:
                    info = json.loads(mark.read_text(encoding='utf-8'))
                    stat = files[0].stat()
                    if (info.get('file') != files[0].name or
                        int(info.get('size', -1)) != stat.st_size or
                        int(info.get('mtime_ns', -1)) != stat.st_mtime_ns):
                        raise ValueError('fichier modifié depuis la dernière sauvegarde')
                except (OSError, ValueError, TypeError, KeyError) as exc:
                    raise RuntimeError(f"Slot interne {slot} non reconnu comme notre AutoSave: {exc}") from exc
            elif mark.exists():
                # Old marker but no state. No conflicting file, so safe to reuse.
                pass


    def list_recoverable(self) -> list[dict]:
        """Only expose states with our signed-by-metadata file identity.

        This is *not* a cryptographic signature; it is an exact file size/time
        match that ensures a foreign/manual state cannot be loaded by mistake.
        """
        result = []
        if not self.path.is_dir():
            return result
        for slot in AUTOSAVE_SLOTS:
            mark = self._marker(slot)
            if not mark.is_file():
                continue
            try:
                meta = json.loads(mark.read_text(encoding='utf-8'))
                files = self._files_in_slot(slot)
                if len(files) != 1 or files[0].name != meta.get('file'):
                    continue
                st = files[0].stat()
                if st.st_size != int(meta['size']) or st.st_mtime_ns != int(meta['mtime_ns']):
                    continue
                if st.st_size < 50_000:
                    continue
                result.append({'slot': slot, 'path': files[0], 'date': str(meta.get('saved_at', '')),
                               'mtime_ns': st.st_mtime_ns, 'size': st.st_size,
                               'ap_identity': str(meta.get('ap_identity', '')),
                               'session_tag': str(meta.get('session_tag', ''))})
            except (OSError, ValueError, TypeError, KeyError):
                continue
        return sorted(result, key=lambda x: x['mtime_ns'], reverse=True)

    def latest_current_session(self, ap_identity: str) -> dict | None:
        """Do not auto-restore legacy markers or states saved in a previous run."""
        if not ap_identity or self.pending_verification is not None:
            return None
        for entry in self.list_recoverable():
            if (entry.get('ap_identity') == ap_identity and
                    entry.get('session_tag') == self.session_tag):
                return {'slot': entry['slot'], 'filename': entry['path'].name,
                        'size': entry['size'], 'mtime_ns': entry['mtime_ns'],
                        'ap_identity': ap_identity}
        return None

    def matches_current_session(self, slot: int, ap_identity: str) -> bool:
        return any(e['slot'] == slot and e.get('ap_identity') == ap_identity and
                   e.get('session_tag') == self.session_tag
                   for e in self.list_recoverable())

    def verify_reload_slot(self, slot: int) -> Path:
        """Check a user-selected automatic slot before issuing PINE LoadState."""
        valid = {e['slot']: e['path'] for e in self.list_recoverable()}
        if slot not in valid:
            raise RuntimeError(f'AutoSave slot {slot} missing or modified; reload refused.')
        if self.pending_verification is not None:
            raise RuntimeError('AutoSave is still writing to disk; reload refused.')
        import zipfile
        with zipfile.ZipFile(valid[slot]) as zf:
            if not zf.infolist():
                raise RuntimeError('Savestate archive empty; reload refused.')
        return valid[slot]

    def _say(self, key: str, **fmt) -> str:
        messages = {
            'en': {
                'on':'AUTO SAVE ON: every 2 min and after zone change; internal slots {start}-{end}; manual slots 0-9 never used.',
                'off':'AUTO SAVE OFF: automatic saving paused.',
                'confirmed':'AUTO SAVE CONFIRMED: {file} (internal slot {slot}).',
                'failed':'AUTO SAVE STOPPED: slot {slot} not confirmed on disk in {path}.',
                'zone':'AUTO SAVE zone: {old} -> {new}; waiting for a stable arrival.',
                'stop':'AUTO SAVE STOPPED: {error}',
                'request':'AUTO SAVE requested ({reason}): internal slot {slot}; awaiting file confirmation.',
                'reason_zone':'zone change', 'reason_time':'2 minutes'},
            'fr': {
                'on':'AUTO SAVE ACTIVÉ : toutes les 2 min et après changement de zone ; slots internes {start}-{end} ; slots 0-9 préservés.',
                'off':'AUTO SAVE DÉSACTIVÉ : sauvegardes suspendues.',
                'confirmed':'AUTO SAVE CONFIRMÉ : {file} (slot interne {slot}).',
                'failed':'AUTO SAVE ARRÊTÉ : slot {slot} non confirmé sur le disque dans {path}.',
                'zone':'AUTO SAVE zone : {old} -> {new} ; attente de stabilisation.',
                'stop':'AUTO SAVE ARRÊTÉ : {error}',
                'request':'AUTO SAVE demandé ({reason}) : slot interne {slot} ; attente du fichier.',
                'reason_zone':'changement de zone', 'reason_time':'2 minutes'},
            'de': {
                'on':'AUTO SAVE AN: alle 2 Min. und nach Gebietswechsel; interne Slots {start}-{end}; manuelle Slots 0-9 bleiben frei.',
                'off':'AUTO SAVE AUS: automatische Speicherung pausiert.',
                'confirmed':'AUTO SAVE BESTÄTIGT: {file} (interner Slot {slot}).',
                'failed':'AUTO SAVE GESTOPPT: Slot {slot} nicht auf Datenträger bestätigt ({path}).',
                'zone':'AUTO SAVE Gebiet: {old} -> {new}; warte auf stabile Ankunft.',
                'stop':'AUTO SAVE GESTOPPT: {error}',
                'request':'AUTO SAVE angefordert ({reason}): Slot {slot}; Dateibestätigung ausstehend.',
                'reason_zone':'Gebietswechsel', 'reason_time':'2 Minuten'},
            'es': {
                'on':'AUTO SAVE ACTIVADO: cada 2 min y tras cambiar de zona; ranuras internas {start}-{end}; las manuales 0-9 intactas.',
                'off':'AUTO SAVE DESACTIVADO: guardado pausado.',
                'confirmed':'AUTO SAVE CONFIRMADO: {file} (ranura interna {slot}).',
                'failed':'AUTO SAVE DETENIDO: ranura {slot} sin confirmar en {path}.',
                'zone':'AUTO SAVE zona: {old} -> {new}; esperando llegada estable.',
                'stop':'AUTO SAVE DETENIDO: {error}',
                'request':'AUTO SAVE solicitado ({reason}): ranura {slot}; pendiente de confirmar archivo.',
                'reason_zone':'cambio de zona', 'reason_time':'2 minutos'},
            'it': {
                'on':'AUTO SAVE ATTIVO: ogni 2 min e dopo cambio zona; slot interni {start}-{end}; slot manuali 0-9 intatti.',
                'off':'AUTO SAVE DISATTIVO: salvataggi sospesi.',
                'confirmed':'AUTO SAVE CONFERMATO: {file} (slot interno {slot}).',
                'failed':'AUTO SAVE INTERROTTO: slot {slot} non confermato su disco in {path}.',
                'zone':'AUTO SAVE zona: {old} -> {new}; attesa di arrivo stabile.',
                'stop':'AUTO SAVE INTERROTTO: {error}',
                'request':'AUTO SAVE richiesto ({reason}): slot {slot}; attesa conferma file.',
                'reason_zone':'cambio zona', 'reason_time':'2 minuti'},
        }
        table = messages.get(self.language, messages['en'])
        return table[key].format(**fmt)

    def set_enabled(self, enabled: bool) -> None:
        if enabled:
            self._preflight()
            self.enabled = True
            now = self.clock()
            self.next_periodic_at = now + INTERVAL_SECONDS
            self.last_request_at = now
            self.pending_zone_save = False
            self.previous = None
            self.next_sample_at = 0.0
            self.pending_verification = None
            self.log(self._say('on', start=AUTOSAVE_SLOTS[0], end=AUTOSAVE_SLOTS[-1]), 'ok')
        else:
            self.enabled = False
            self.pending_verification = None
            self.log(self._say('off'), 'info')

    def _skip(self, text: str, now: float):
        if (text != self.last_skip_note or now - self.last_skip_at >= 90.0):
            self.last_skip_note, self.last_skip_at = text, now
            # Do not spam normal log: only exceptional conditions are logged.

    def _verify_pending(self, now: float) -> bool:
        if self.pending_verification is None:
            return False
        slot, requested_at, before = self.pending_verification
        if now - requested_at < 3.0:
            return True
        for f in self._files_in_slot(slot):
            st = f.stat()
            older = before.get(f.name)
            if st.st_size < 50_000:
                continue
            if older is not None and older == (st.st_size, st.st_mtime_ns):
                continue
            # Zip file may still be being written asynchronously. Once the zip
            # validates, its central directory was committed to disk.
            try:
                import zipfile
                with zipfile.ZipFile(f) as archive:
                    members = archive.infolist()
                    if not members:
                        continue
                    # Only a small entry: a full testzip() can block the PINE
                    # owner thread for seconds on large savestates.
                    tiny = next((m for m in members if m.file_size <= 16384 and not m.is_dir()), None)
                    if tiny is not None:
                        archive.read(tiny)
            except (OSError, zipfile.BadZipFile, RuntimeError):
                continue
            stat = f.stat()
            data = {'file': f.name, 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns,
                    'slot': slot, 'saved_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'ap_identity': self.pending_identity, 'session_tag': self.session_tag}
            marker = self._marker(slot)
            tmp = marker.with_suffix('.tmp')
            tmp.write_text(json.dumps(data, indent=2), encoding='utf-8')
            tmp.replace(marker)
            self.pending_verification = None
            self.pending_identity = ''
            self.next_slot = (self.next_slot + 1) % len(AUTOSAVE_SLOTS)
            self.log(self._say('confirmed', file=f.name, slot=slot), 'ok')
            return False
        if now - requested_at > VERIFICATION_TIMEOUT_SECONDS:
            self.pending_verification = None
            self.enabled = False
            self.log(self._say('failed', slot=slot, path=self.path), 'error')
        return True

    def tick(self, pine, zone: str | None, generation: tuple[int, int] | None,
             blocked: bool = False) -> None:
        if not self.enabled:
            return
        now = self.clock()
        # Even if transitioning, check previous asynchronous save completion.
        if self._verify_pending(now):
            return
        if blocked or not zone or not generation or now < self.next_sample_at:
            return
        self.next_sample_at = now + SAMPLE_PERIOD
        try:
            status_data = pine._packet(b'\x0f')
            if len(status_data) < 4 or struct.unpack('<I', status_data[:4])[0] != 0:
                return
            # V0.9.46: 0x00451ABC is also activated by regeneration ambers.
            # Do not let the pseudo-MAP flag block AutoSave. Stable actors,
            # recent genuine movement, VM status, and 15s stream settling
            # remain mandatory before PCSX2 receives a SaveState request.
            values = pine.read32_many([ACTOR_ADDR, PLAYER_ADDR])
            actor, player = map(int, values)
            if not _ptr_ok(actor) or actor != player:
                return
            state_data = pine.read32_many([actor + 0x104, actor + 0x30,
                                           actor + 0x34, actor + 0x38])
            state = int(state_data[0])
            position = tuple(_float32(int(n)) for n in state_data[1:])
            if not all(math.isfinite(v) and abs(v) < 100000 for v in position):
                return
        except Exception as exc:
            self._skip(f"lecture PINE impossible: {exc}", now)
            return

        cur = Frame(now, zone, generation, actor, state, position)
        prev = self.previous
        self.previous = cur
        if prev is None:
            self.zone_since = self.generation_since = now
            return
        if zone != prev.zone:
            self.zone_since = now
            self.pending_zone_save = True
            self.still_since = 0.0
            self.moved_at = -float('inf')
            self.move_states.clear()
            self.log(self._say('zone', old=prev.zone, new=zone), 'info')
            return
        if generation != prev.generation or actor != prev.actor:
            self.generation_since = now
            self.still_since = 0.0
            self.moved_at = -float('inf')
            self.move_states.clear()
            return
        if now - self.zone_since < ZONE_SETTLE_SECONDS or now - self.generation_since < STREAM_SETTLE_SECONDS:
            return
        distance = math.dist(position, prev.position)
        if distance > 40:
            self.generation_since = now
            self.still_since = 0.0
            self.moved_at = -float('inf')
            self.move_states.clear()
            return
        if distance > 0.65:
            self.moved_at = now
            self.move_states[state] = now
            self.still_since = 0.0
            # A zone-change save should not require Kya to stop walking.
            # Once the zone and actor generation have both been stable for
            # 15 seconds, genuine player movement is sufficient. PCSX2 owns
            # the snapshot and freezes its VM while taking it. Periodic saves
            # retain the stricter idle guard below.
            if not self.pending_zone_save:
                return
        elif not self.still_since:
            self.still_since = now
        if not self.pending_zone_save and now - self.still_since < MIN_STILL_SECONDS:
            return
        if now - self.moved_at > RECENT_MOVEMENT_SECONDS or state not in self.move_states:
            return
        if (not self.pending_zone_save and now < self.next_periodic_at):
            return
        if now - self.last_request_at < MIN_SAVE_GAP_SECONDS:
            return
        slot = AUTOSAVE_SLOTS[self.next_slot]
        # Catch a new conflicting file before any write -- not just at startup.
        try:
            self._preflight()
            before = {f.name: (f.stat().st_size, f.stat().st_mtime_ns)
                      for f in self._files_in_slot(slot)}
            if slot in range(10):
                raise RuntimeError('Slot manuel interdit')
            response = pine._packet(bytes((9, slot)))
            if response:
                raise RuntimeError('Réponse MsgSaveState inattendue')
        except Exception as exc:
            self.enabled = False
            self.log(self._say('stop', error=exc), 'error')
            return
        self.last_request_at = now
        self.next_periodic_at = now + INTERVAL_SECONDS
        reason = self._say('reason_zone') if self.pending_zone_save else self._say('reason_time')
        self.pending_zone_save = False
        self.pending_verification = (slot, now, before)
        self.pending_identity = self.ap_identity
        self.log(self._say('request', reason=reason, slot=slot), 'info')
