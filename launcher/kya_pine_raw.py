from __future__ import annotations
import socket
import struct
import time

READ32 = 0x02
WRITE32 = 0x06

class PineError(RuntimeError):
    pass

class PineClient:
    def __init__(self, host="127.0.0.1", port=28011, timeout=8.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self):
        self.close()
        self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.sock.settimeout(self.timeout)
        return self

    def close(self):
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _recv_exact(self, n):
        out = bytearray()
        while len(out) < n:
            try:
                part = self.sock.recv(n - len(out))
            except OSError as e:
                self.close()
                raise PineError(f"Connexion PINE perdue pendant la lecture: {e}") from e
            if not part:
                self.close()
                raise PineError("Connexion PINE fermee pendant la lecture.")
            out.extend(part)
        return bytes(out)

    def _packet(self, commands: bytes) -> bytes:
        if self.sock is None:
            raise PineError("PINE non connecte.")
        packet = struct.pack("<I", 4 + len(commands)) + commands
        try:
            self.sock.sendall(packet)
        except OSError as e:
            self.close()
            raise PineError(f"Connexion PINE perdue: {e}") from e

        size = struct.unpack("<I", self._recv_exact(4))[0]
        if size < 5:
            raise PineError(f"Reponse PINE invalide: taille={size}")
        body = self._recv_exact(size - 4)
        status = body[0]
        if status != 0:
            raise PineError(f"PINE a retourne le statut d'erreur 0x{status:02X}.")
        return body[1:]

    def read32(self, address: int) -> int:
        payload = self._packet(bytes([READ32]) + struct.pack("<I", address & 0xFFFFFFFF))
        if len(payload) < 4:
            raise PineError("Reponse Read32 trop courte.")
        return struct.unpack_from("<I", payload, 0)[0]

    def read32_many(self, addresses, batch_size=4096):
        addresses = list(addresses)
        result = []
        for start in range(0, len(addresses), batch_size):
            batch = addresses[start:start + batch_size]
            commands = bytearray()
            for addr in batch:
                commands.append(READ32)
                commands += struct.pack("<I", addr & 0xFFFFFFFF)
            payload = self._packet(bytes(commands))
            expected = len(batch) * 4
            if len(payload) < expected:
                raise PineError(
                    f"Reponse multi-Read32 trop courte ({len(payload)} < {expected})."
                )
            result.extend(struct.unpack("<" + "I" * len(batch), payload[:expected]))
        return result

    def write32(self, address: int, value: int):
        commands = bytes([WRITE32]) + struct.pack(
            "<II", address & 0xFFFFFFFF, value & 0xFFFFFFFF
        )
        self._packet(commands)

def scan_value32(
    pine: PineClient,
    value: int,
    start=0x01000000,
    end=0x02000000,
    step=0x20,
    batch_reads=4096,
    progress=None,
):
    hits = []
    total = max(1, (end - start + step - 1) // step)
    done = 0
    cursor = start
    while cursor < end:
        addrs = []
        for _ in range(batch_reads):
            if cursor >= end:
                break
            addrs.append(cursor)
            cursor += step
        vals = pine.read32_many(addrs, batch_size=batch_reads)
        for a, v in zip(addrs, vals):
            if v == value:
                hits.append(a)
        done += len(addrs)
        if progress:
            progress(done, total, len(hits))
    return hits

def contiguous_chains(hits, stride):
    hitset = set(hits)
    chains = []
    for h in sorted(hits):
        if h - stride in hitset:
            continue
        cur = h
        chain = []
        while cur in hitset:
            chain.append(cur)
            cur += stride
        chains.append(chain)
    return sorted(chains, key=lambda c: (-len(c), c[0] if c else 0))

def resolve_descriptor_candidate_key(pine: PineClient, actor: int):
    desc = pine.read32(actor + 0x1C)
    if not (0x00100000 <= desc < 0x02000000):
        return desc, None
    try:
        key = pine.read32(desc + 0x28)
    except Exception:
        return desc, None
    return desc, key
