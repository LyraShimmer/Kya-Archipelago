from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

CORE_HOST = "127.0.0.1"
CORE_PORT = 28111
_OWNED_PROCESS: subprocess.Popen | None = None


def _port_open(timeout: float = 0.15) -> bool:
    try:
        with socket.create_connection((CORE_HOST, CORE_PORT), timeout=timeout):
            return True
    except OSError:
        return False


def _base_dirs() -> list[Path]:
    dirs: list[Path] = []
    if getattr(sys, "frozen", False):
        dirs.append(Path(sys.executable).resolve().parent)
    try:
        dirs.append(Path(__file__).resolve().parent)
    except Exception:
        pass
    if hasattr(sys, "_MEIPASS"):
        dirs.append(Path(getattr(sys, "_MEIPASS")))
    # stable de-duplication
    out: list[Path] = []
    seen = set()
    for d in dirs:
        key = str(d)
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def ensure_memory_core(timeout: float = 5.0) -> tuple[bool, str]:
    """Ensure the dedicated MemoryCore proxy is listening.

    Returns (started_by_us, description).  If a core is already present we reuse
    it, which also makes accidental double-launches harmless.
    """
    global _OWNED_PROCESS
    if _port_open():
        return False, f"MemoryCore already active on {CORE_HOST}:{CORE_PORT}"

    exe = None
    script = None
    for base in _base_dirs():
        candidate = base / "Kya_MemoryCore.exe"
        if candidate.exists():
            exe = candidate
            break
    if exe is None:
        for base in _base_dirs():
            candidate = base / "kya_memory_core.py"
            if candidate.exists():
                script = candidate
                break

    if exe is None and script is None:
        raise RuntimeError(
            "Kya_MemoryCore was not found next to the Launcher. "
            "Keep Kya_MemoryCore.exe (or kya_memory_core.py in source mode) in the same folder."
        )

    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

    parent_args = ["--parent-pid", str(os.getpid())]
    if exe is not None:
        cmd = [str(exe), *parent_args]
        cwd = exe.parent
    else:
        cmd = [sys.executable, str(script), *parent_args]
        cwd = script.parent

    _OWNED_PROCESS = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
        startupinfo=startupinfo,
    )

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _port_open():
            return True, f"MemoryCore started on {CORE_HOST}:{CORE_PORT}"
        if _OWNED_PROCESS.poll() is not None:
            raise RuntimeError(
                f"Kya_MemoryCore exited immediately with code {_OWNED_PROCESS.returncode}. "
                "See logs/Kya_MemoryCore.log."
            )
        time.sleep(0.05)

    raise RuntimeError(
        f"Kya_MemoryCore did not become ready on {CORE_HOST}:{CORE_PORT} within {timeout:.1f}s."
    )


def stop_owned_memory_core() -> None:
    global _OWNED_PROCESS
    proc = _OWNED_PROCESS
    _OWNED_PROCESS = None
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=1.5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
