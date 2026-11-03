"""Small Archipelago WebSocket link used by the standalone Kya Launcher."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import queue
import socket
import ssl
import struct
import threading
import time
from urllib.parse import urlparse

GAME = "Kya: Dark Lineage"
VERSION = {"class": "Version", "major": 0, "minor": 6, "build": 7}


class APLink:
    def __init__(self, address: str, slot: str, password: str = ""):
        self.address, self.slot, self.password = address, slot, password or None
        self.events: queue.Queue = queue.Queue()
        self.outgoing: queue.Queue = queue.Queue()
        self.stop_event = threading.Event()
        self.connected_event = threading.Event()
        self.room_seed = ""
        self.thread: threading.Thread | None = None
        self.sock: socket.socket | None = None
        self._send_lock = threading.Lock()
        self._item_index = 0
        self._known_checked: set[int] = set()
        # HTTP upgrade and first WebSocket frame may arrive in one TCP recv().
        self._recv_buffer = bytearray()

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True, name="KyaAPLink")
        self.thread.start()

    def close(self):
        self.stop_event.set()
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def check(self, location_id: int):
        self.outgoing.put({"cmd": "LocationChecks", "locations": [int(location_id)]})

    def goal(self):
        """Tell the Archipelago server that the game goal was reached."""
        self.outgoing.put({"cmd": "StatusUpdate", "status": 30})

    def _send_frame(self, payload: bytes, opcode=1):
        if not self.sock:
            # Never silently discard LocationChecks/StatusUpdate when the socket
            # drops between dequeue and send; the caller will requeue it.
            raise ConnectionError("Archipelago WebSocket is not connected")
        n = len(payload)
        head = bytes([0x80 | opcode])
        mask = os.urandom(4)
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack("!H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack("!Q", n)
        masked = bytes(b ^ mask[i & 3] for i, b in enumerate(payload))
        with self._send_lock:
            self.sock.sendall(head + mask + masked)

    def _send_json(self, obj):
        self._send_frame(json.dumps([obj], separators=(",", ":")).encode())

    def _recv_exact(self, n, *, continue_on_timeout=False):
        out = bytearray()
        if self._recv_buffer:
            use = min(n, len(self._recv_buffer))
            out.extend(self._recv_buffer[:use])
            del self._recv_buffer[:use]
        while len(out) < n and not self.stop_event.is_set():
            try:
                part = self.sock.recv(n-len(out))
            except socket.timeout:
                # An idle socket should return control to the event loop, but
                # once a frame has begun, its bytes must NOT be thrown away.
                if not out and not continue_on_timeout:
                    raise
                continue
            if not part:
                raise ConnectionError("Archipelago server closed the connection")
            out.extend(part)
        if len(out) != n:
            raise ConnectionError("Archipelago connection stopped")
        return bytes(out)

    def _recv_frame(self):
        # Read both header bytes atomically so a timeout between them cannot
        # desynchronize the next frame.
        first, second = self._recv_exact(2)
        opcode, length = first & 15, second & 127
        if length == 126: length = struct.unpack("!H", self._recv_exact(2, continue_on_timeout=True))[0]
        elif length == 127: length = struct.unpack("!Q", self._recv_exact(8, continue_on_timeout=True))[0]
        mask = self._recv_exact(4, continue_on_timeout=True) if second & 128 else None
        data = self._recv_exact(length, continue_on_timeout=True)
        if mask: data = bytes(b ^ mask[i & 3] for i,b in enumerate(data))
        if opcode == 9:
            self._send_frame(data, 10)
            return self._recv_frame()
        if opcode == 8: raise ConnectionError("Archipelago server closed WebSocket")
        return data

    def _run(self):
        """Keep AP online independently of PCSX2; retry transport failures."""
        delay = 2.0
        while not self.stop_event.is_set():
            self._item_index = 0  # Each new AP session receives full history at index 0.
            self._known_checked.clear()
            self._run_session()
            if self.stop_event.is_set():
                break
            self.events.put(("link_lost", "Archipelago connection lost; automatic retry active."))
            self.events.put(("status", f"Archipelago retry in {int(delay)}s (game may be offline)."))
            if self.stop_event.wait(delay):
                break
            delay = min(20.0, delay * 1.7)

    def _run_session(self):
        try:
            has_scheme = "://" in self.address
            parsed = urlparse(self.address if has_scheme else "ws://" + self.address)
            host, port = parsed.hostname or "localhost", parsed.port or 38281
            path = parsed.path or "/"
            schemes = ["wss"] if parsed.scheme.lower() == "wss" else ["ws", "wss"]
            errors = []

            self._recv_buffer.clear()
            for scheme in schemes:
                raw_sock = None
                sock = None
                try:
                    raw_sock = socket.create_connection((host, port), timeout=8)
                    if scheme == "wss":
                        context = ssl.create_default_context()
                        sock = context.wrap_socket(raw_sock, server_hostname=host)
                    else:
                        sock = raw_sock
                    sock.settimeout(8)

                    key = base64.b64encode(os.urandom(16)).decode()
                    request = (
                        f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\n"
                        "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
                    )
                    sock.sendall(request.encode())
                    response = bytearray()
                    while b"\r\n\r\n" not in response and len(response) < 8192:
                        chunk = sock.recv(1024)
                        if not chunk:
                            raise ConnectionError(f"Server closed during {scheme.upper()} WebSocket handshake.")
                        response.extend(chunk)

                    response_bytes = bytes(response)
                    if b"\r\n\r\n" not in response_bytes:
                        raise ConnectionError("Incomplete WebSocket upgrade response")
                    head_bytes, first_frame_bytes = response_bytes.split(b"\r\n\r\n", 1)
                    head = head_bytes.decode("latin1")
                    expected = base64.b64encode(
                        hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
                    ).decode()
                    # HTTP header names are case-insensitive; check the value
                    # on the exact Sec-WebSocket-Accept header, not a substring.
                    headers = {}
                    for header_line in head.splitlines()[1:]:
                        if ":" in header_line:
                            name, value = header_line.split(":", 1)
                            headers[name.strip().lower()] = value.strip()
                    if " 101 " not in head.splitlines()[0] or headers.get("sec-websocket-accept") != expected:
                        raise ConnectionError("WebSocket upgrade failed: " + (head.splitlines()[0] if head else "empty response"))

                    self._recv_buffer.extend(first_frame_bytes)
                    self.sock = sock
                    self.sock.settimeout(0.10)
                    break
                except Exception as exc:
                    errors.append(f"{scheme}: {type(exc).__name__}: {exc}")
                    for candidate in (sock, raw_sock):
                        if candidate is not None:
                            try:
                                candidate.close()
                            except OSError:
                                pass
            if self.sock is None:
                raise ConnectionError("; ".join(errors))
            self.events.put(("status", "Connected to Archipelago; joining slot…"))
            self._send_json({"cmd":"Connect","password":self.password,"game":GAME,"name":self.slot,
                "uuid":"kya-launcher-v1","version":VERSION,"items_handling":7,"tags":["AP"],"slot_data":True})
            while not self.stop_event.is_set():
                try:
                    raw = self._recv_frame()
                    packets = json.loads(raw.decode("utf-8"))
                    for packet in packets:
                        cmd = packet.get("cmd")
                        if cmd == "RoomInfo":
                            self.room_seed = str(packet.get("seed_name") or "").strip()
                            self.events.put(("roominfo", packet))
                        elif cmd == "Connected":
                            self.connected_event.set()
                            self._item_index = 0  # Connected is not ReceivedItems; replay server stream from index 0
                            self._known_checked = {int(x) for x in packet.get("checked_locations", [])}
                            self.events.put(("joined", packet))
                        elif cmd == "RoomUpdate":
                            if "checked_locations" in packet:
                                self._known_checked.update(int(x) for x in packet.get("checked_locations", []))
                            self.events.put(("room_update", packet))
                        elif cmd == "ConnectionRefused":
                            errors = ", ".join(packet.get("errors", []))
                            self.events.put(("error", "Slot refused: " + errors))
                            self.stop_event.set()
                            return
                        elif cmd == "ReceivedItems":
                            start = int(packet.get("index", 0))
                            for offset, item in enumerate(packet.get("items", [])):
                                absolute_index = start + offset
                                if absolute_index >= self._item_index:
                                    if isinstance(item, dict):
                                        enriched = dict(item)
                                    else:
                                        enriched = {
                                            "item": item[0],
                                            "location": item[1] if len(item) > 1 else -1,
                                            "player": item[2] if len(item) > 2 else 0,
                                            "flags": item[3] if len(item) > 3 else 0,
                                        }
                                    enriched["_ap_index"] = absolute_index
                                    self.events.put(("item", enriched))
                            self._item_index = max(self._item_index, start + len(packet.get("items", [])))
                        elif cmd == "PrintJSON":
                            # Keep the complete packet so the Launcher can distinguish
                            # ItemSend trades from chat/join/hint messages for its overlay.
                            self.events.put(("printjson", packet))
                except socket.timeout:
                    pass
                # Do not drain queued checks before the AP server has accepted
                # the slot (Connected); otherwise early packets can be dropped.
                if self.connected_event.is_set():
                    while True:
                        try: packet = self.outgoing.get_nowait()
                        except queue.Empty: break
                        try:
                            self._send_json(packet)
                        except Exception:
                            self.outgoing.put(packet)  # LocationChecks are idempotent at the server.
                            raise
        except Exception as exc:
            if not self.stop_event.is_set(): self.events.put(("status", f"AP connection issue: {type(exc).__name__}: {exc}"))
        finally:
            self.connected_event.clear()
            self.room_seed = ""
            self._recv_buffer.clear()
            try:
                if self.sock: self.sock.close()
            except OSError: pass
            self.sock = None
