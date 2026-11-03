"""Read-only menu/MAP guard with movement-validated recovery.

PCSX2 PAL Kya uses 0x00451ABC for a MAP-associated state, but the same
value 1 also appears near regeneration ambers (confirmed by a live player).
It must NEVER be treated as positive proof that the map is open. The old binary MAP gate permanently
starved all AP checks and goal polling. We do NOT blindly ignore the bit:
only verified movement of Kya's *actor position* can override it.

No reads from native PCSX2 are owned here: the main Launcher PINE service
passes its single existing PINE owner into this helper.
"""
from __future__ import annotations

import math
import struct


def _float32(bits: int) -> float:
    return struct.unpack('<f', struct.pack('<I', int(bits) & 0xFFFFFFFF))[0]


class MapGuardRecovery:
    """One PINE-owner-only gate; ``update`` returns (paused, event)."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.map_since = None
        self.last_actor = None
        self.last_position = None
        self.last_sample = 0.0
        self.distance = 0.0
        self.last_motion = 0.0
        self.override = False
        self.paused = False

    @property
    def false_positive_confirmed(self) -> bool:
        return self.override

    def update(self, pine, d: dict, value: int, now: float) -> tuple[bool, str | None]:
        if value == 0:
            was_paused = self.paused
            self.reset()
            return False, ('MAP closed; Launcher watchers resume.' if was_paused else None)

        if self.map_since is None:
            self.map_since = now
            self.paused = True
            return True, f'MAP/amber flag active (state=0x{value:08X}); verifying gameplay movement before AP writes.'

        # Validate two independent global pointers (same Kya actor). This is
        # read-only; reject cutscenes/streams where they differ or disappear.
        try:
            kya, player = (int(v) for v in pine.read32_many([
                int(d['ADDR_KYA_ACTOR_GLOBAL']), int(d['ADDR_PLAYER_POINTER'])]))
            if (kya != player or kya < 0x00100000 or kya >= 0x02000000 or kya & 3):
                raise ValueError('Kya actor not established')
            raw = pine.read32_many([
                kya + int(d['ACTOR_POS_X_OFFSET']),
                kya + int(d['ACTOR_POS_Y_OFFSET']),
                kya + int(d['ACTOR_POS_Z_OFFSET']),
            ])
            pos = tuple(_float32(v) for v in raw)
            if not all(math.isfinite(p) and abs(p) < 100000.0 for p in pos):
                raise ValueError('invalid Kya position')
        except (ValueError, TypeError, KeyError, OverflowError, struct.error, RuntimeError):
            # A partial/invalid scene must never permit memory writers.
            if self.override:
                self.override = False
                self.distance = 0.0
                self.last_position = None
                self.last_actor = None
                self.paused = True
                return True, 'MAP guard: player actor unavailable; AP writes paused.'
            self.paused = True
            return True, None

        if self.last_actor != kya:
            # Savestate and zone loads replace runtime actors. Do not inherit
            # movement authorization from the previous scene.
            was_override = self.override
            self.last_actor = kya
            self.last_position = pos
            self.last_sample = now
            self.distance = 0.0
            self.last_motion = 0.0
            self.override = False
            self.map_since = now
            self.paused = True
            return True, ('MAP guard reset: new player actor/scene; observing Kya movement.'
                          if was_override else None)

        delta = 0.0
        if self.last_position is not None and 0 < now - self.last_sample <= 2.0:
            delta = math.dist(pos, self.last_position)
        self.last_position, self.last_sample = pos, now
        # Reject jumps/teleports as gameplay movement evidence.
        genuine_motion = 0.08 <= delta <= 5.0
        if genuine_motion:
            self.last_motion = now
            self.distance += delta

        if not self.override and now - self.map_since >= 2.0 and self.distance >= 2.0:
            self.override = True
            self.paused = False
            return False, ('MAP/amber flag=1 with >=2m validated Kya movement: '
                           'resuming AP watchers (gameplay-motion guard; real menus still pause).')

        if self.override:
            # Amber regeneration can leave this bit set while Kya stops to
            # interact. Allow a bounded idle grace after verified walking.
            # Since 1 ALSO means map, never leave writers running indefinitely:
            # after 12s idle pause again until movement is independently seen.
            # A fully reliable MAP-vs-amber test needs a second game signal.
            if now - self.last_motion > 12.0:
                if not self.paused:
                    self.paused = True
                    return True, 'MAP/amber flag still 1 and Kya idle; pausing uncertain AP memory writes.'
                return True, None
            if self.paused:
                self.paused = False
                return False, 'Kya moving again with stale MAP flag: AP watchers resumed.'
            return False, None

        self.paused = True
        return True, None
