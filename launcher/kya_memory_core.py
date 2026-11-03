from __future__ import annotations

"""Kya MemoryCore V0.9.0

Transparent local PINE proxy.

The Launcher connects to 127.0.0.1:28111.  This process is the *only* process
that connects to PCSX2's real PINE endpoint on 127.0.0.1:28011.  Every PINE
request/response is serialized through one lock and one real socket.

Keeping the protocol transparent means the proven V0.8.49 Fast Travel timing
code does not need to be rewritten for this architecture test.
"""

import os
import socket
import struct
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

CORE_HOST = "127.0.0.1"
CORE_PORT = 28111
PCSX2_HOST = "127.0.0.1"
PCSX2_PINE_PORT = 28011
SOCKET_TIMEOUT = 8.0


class MemoryCore:
    def __init__(self, parent_pid: int | None = None) -> None:
        self._pine_sock: socket.socket | None = None
        self._pine_lock = threading.RLock()
        self._stop = threading.Event()
        self._clients: set[socket.socket] = set()
        self._clients_lock = threading.Lock()
        self._log_lock = threading.Lock()
        self._log_path = self._make_log_path()
        self._parent_pid = int(parent_pid) if parent_pid else None

    @staticmethod
    def _make_log_path() -> Path:
        if getattr(__import__('sys'), 'frozen', False):
            base = Path(__import__('sys').executable).resolve().parent
        else:
            base = Path(__file__).resolve().parent
        log_dir = base / "logs"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            return log_dir / "Kya_MemoryCore.log"
        except Exception:
            return Path(os.getenv("TEMP") or ".") / "Kya_MemoryCore.log"

    def log(self, message: str) -> None:
        line = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}"
        with self._log_lock:
            try:
                with self._log_path.open("a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            except Exception:
                pass

    @staticmethod
    def _recv_exact(sock: socket.socket, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            chunk = sock.recv(n - len(out))
            if not chunk:
                raise ConnectionError("socket closed")
            out.extend(chunk)
        return bytes(out)

    def _close_real_pine(self) -> None:
        if self._pine_sock is not None:
            try:
                self._pine_sock.close()
            except OSError:
                pass
        self._pine_sock = None

    def _ensure_real_pine(self) -> socket.socket:
        if self._pine_sock is not None:
            return self._pine_sock
        sock = socket.create_connection((PCSX2_HOST, PCSX2_PINE_PORT), timeout=SOCKET_TIMEOUT)
        sock.settimeout(SOCKET_TIMEOUT)
        self._pine_sock = sock
        self.log(f"Connected to real PCSX2 PINE {PCSX2_HOST}:{PCSX2_PINE_PORT}.")
        return sock

    @staticmethod
    def _pid_alive(pid: int) -> bool:
        if pid <= 0:
            return False
        if os.name == "nt":
            try:
                import ctypes
                from ctypes import wintypes
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                STILL_ACTIVE = 259
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
                if not handle:
                    return False
                try:
                    code = wintypes.DWORD()
                    if not kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                        return False
                    return int(code.value) == STILL_ACTIVE
                finally:
                    kernel32.CloseHandle(handle)
            except Exception:
                return True
        try:
            os.kill(int(pid), 0)
            return True
        except OSError:
            return False

    def _watch_parent(self) -> None:
        pid = self._parent_pid
        if not pid:
            return
        self.log(f"Parent watchdog armed for Launcher PID {pid}.")
        while not self._stop.wait(0.35):
            if not self._pid_alive(pid):
                self.log(f"Launcher PID {pid} is gone; shutting MemoryCore down automatically.")
                self._stop.set()
                break

    def _forward_one(self, packet: bytes) -> bytes:
        # This lock is the core architecture invariant: one request at a time,
        # one real PINE owner, regardless of how many launcher-side modules/threads
        # eventually submit work.
        with self._pine_lock:
            real = self._ensure_real_pine()
            try:
                real.sendall(packet)
                header = self._recv_exact(real, 4)
                size = struct.unpack("<I", header)[0]
                if size < 5 or size > 64 * 1024 * 1024:
                    raise ConnectionError(f"invalid PINE response size {size}")
                body = self._recv_exact(real, size - 4)
                return header + body
            except Exception:
                self._close_real_pine()
                raise

    def _handle_client(self, client: socket.socket, addr) -> None:
        client.settimeout(None)
        with self._clients_lock:
            self._clients.add(client)
        self.log(f"Launcher client connected from {addr[0]}:{addr[1]}.")
        try:
            while not self._stop.is_set():
                header = self._recv_exact(client, 4)
                size = struct.unpack("<I", header)[0]
                if size < 5 or size > 64 * 1024 * 1024:
                    raise ConnectionError(f"invalid launcher PINE packet size {size}")
                body = self._recv_exact(client, size - 4)
                response = self._forward_one(header + body)
                client.sendall(response)
        except Exception as exc:
            self.log(f"Launcher client disconnected: {type(exc).__name__}: {exc}")
        finally:
            with self._clients_lock:
                self._clients.discard(client)
            try:
                client.close()
            except OSError:
                pass

    def serve(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((CORE_HOST, CORE_PORT))
        server.listen(8)
        server.settimeout(0.5)
        self.log(
            f"MemoryCore READY on {CORE_HOST}:{CORE_PORT}; exclusive upstream is "
            f"{PCSX2_HOST}:{PCSX2_PINE_PORT}."
        )
        if self._parent_pid:
            threading.Thread(
                target=self._watch_parent,
                daemon=True,
                name="KyaMemoryCoreParentWatch",
            ).start()
        try:
            while not self._stop.is_set():
                try:
                    client, addr = server.accept()
                except socket.timeout:
                    continue
                threading.Thread(
                    target=self._handle_client,
                    args=(client, addr),
                    daemon=True,
                    name="KyaMemoryCoreClient",
                ).start()
        finally:
            self._stop.set()
            try:
                server.close()
            except OSError:
                pass
            with self._clients_lock:
                clients = list(self._clients)
            for client in clients:
                try:
                    client.close()
                except OSError:
                    pass
            with self._pine_lock:
                self._close_real_pine()
            self.log("MemoryCore stopped.")


if __name__ == "__main__":
    _parent_pid = None
    try:
        if "--parent-pid" in sys.argv:
            _i = sys.argv.index("--parent-pid")
            if _i + 1 < len(sys.argv):
                _parent_pid = int(sys.argv[_i + 1])
    except (TypeError, ValueError):
        _parent_pid = None
    try:
        MemoryCore(parent_pid=_parent_pid).serve()
    except OSError as exc:
        # Most commonly: another MemoryCore already owns 28111.  Exiting is
        # intentional; the Launcher will connect to the existing owner.
        try:
            MemoryCore().log(f"MemoryCore could not bind: {exc}")
        except Exception:
            pass
