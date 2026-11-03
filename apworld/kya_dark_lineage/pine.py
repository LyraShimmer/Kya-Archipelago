from __future__ import annotations

import asyncio
import re
import struct
from typing import Optional


class PineError(RuntimeError):
    pass


class PineClient:
    """Small async PCSX2 PINE client implementing only what this prototype needs."""

    MSG_READ32 = 0x02
    MSG_WRITE32 = 0x06
    MSG_ID = 0x0C

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        return self.writer is not None and not self.writer.is_closing()

    async def connect(self) -> None:
        if self.connected:
            return
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def close(self) -> None:
        writer = self.writer
        self.reader = None
        self.writer = None
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def _request(self, payload: bytes) -> bytes:
        if not self.connected or self.reader is None or self.writer is None:
            raise PineError("PINE is not connected.")

        packet = struct.pack("<I", len(payload) + 4) + payload

        async with self._lock:
            try:
                self.writer.write(packet)
                await self.writer.drain()

                header = await self.reader.readexactly(4)
                total_size = struct.unpack("<I", header)[0]
                if total_size < 5:
                    raise PineError(f"Invalid PINE reply size: {total_size}")

                body = await self.reader.readexactly(total_size - 4)
            except (ConnectionError, asyncio.IncompleteReadError, OSError) as exc:
                await self.close()
                raise PineError(f"PINE connection lost: {exc}") from exc

        result = body[0]
        if result != 0x00:
            raise PineError(f"PINE command failed with result 0x{result:02X}.")
        return body[1:]

    async def read32(self, address: int) -> int:
        data = await self._request(struct.pack("<BI", self.MSG_READ32, address))
        if len(data) < 4:
            raise PineError("PINE Read32 reply was too short.")
        return struct.unpack("<I", data[:4])[0]

    async def read32_many(self, addresses: list[int], batch_size: int = 50000) -> list[int]:
        """Read many 32-bit addresses using PINE's multi-command packet format.

        PCSX2 accepts multiple IPC commands in one request packet. Keeping batches
        below 50k Read32 commands stays comfortably under both protocol buffer
        limits while making runtime-pool discovery practical.
        """
        if not addresses:
            return []

        out: list[int] = []
        for start in range(0, len(addresses), batch_size):
            chunk = addresses[start:start + batch_size]
            payload = b"".join(
                struct.pack("<BI", self.MSG_READ32, address) for address in chunk
            )
            data = await self._request(payload)
            expected = len(chunk) * 4
            if len(data) != expected:
                raise PineError(
                    f"PINE batched Read32 reply had {len(data)} bytes; expected {expected}."
                )
            out.extend(struct.unpack(f"<{len(chunk)}I", data))
        return out

    async def find32_aligned(
        self,
        start: int,
        end: int,
        value: int,
        alignment: int = 4,
        scan_batch_size: int = 50000,
    ) -> list[int]:
        """Return aligned addresses in [start, end) whose Read32 equals value."""
        if alignment <= 0:
            raise ValueError("alignment must be positive")

        first = (start + alignment - 1) // alignment * alignment
        hits: list[int] = []
        cursor = first
        span = alignment * scan_batch_size

        while cursor < end:
            chunk_end = min(end, cursor + span)
            addresses = list(range(cursor, chunk_end, alignment))
            values = await self.read32_many(addresses, batch_size=scan_batch_size)
            hits.extend(address for address, got in zip(addresses, values) if got == value)
            cursor = chunk_end

        return hits

    async def write32(self, address: int, value: int) -> None:
        await self._request(
            struct.pack("<BII", self.MSG_WRITE32, address, value & 0xFFFFFFFF)
        )

    async def game_id(self) -> str:
        data = await self._request(bytes([self.MSG_ID]))
        if len(data) < 4:
            raise PineError("PINE game-ID reply was too short.")

        string_size = struct.unpack("<I", data[:4])[0]
        raw = data[4:4 + string_size]
        if len(raw) != string_size:
            raise PineError("PINE game-ID reply was truncated.")

        return raw.rstrip(b"\x00").decode("utf-8", errors="replace")

    @staticmethod
    def normalize_serial(serial: str) -> str:
        return re.sub(r"[^A-Z0-9]", "", serial.upper())
