"""TLS helper for the standalone Kya Launcher.

Why this exists: ssl.create_default_context() on Windows trusts whatever is in the
Windows certificate stores. A stale/expired root or cross-signed chain there makes
hosted rooms (wss://archipelago.gg) fail with "certificate has expired" while
Archipelago's own client works, because that client verifies against the certifi
CA bundle. We do the same: certifi first, then the OS store as a fallback.
Certificate verification is NEVER disabled.

Optional override: set KYA_CA_BUNDLE to a PEM file path to add a trusted CA bundle
(first in the list), e.g. for a self-hosted room with a private CA.
"""
from __future__ import annotations

import os
import socket
import ssl


def _ctx_from_cafile(cafile: str) -> ssl.SSLContext | None:
    try:
        return ssl.create_default_context(cafile=cafile)
    except Exception:
        return None


def make_ssl_contexts() -> list[ssl.SSLContext]:
    """Verifying contexts to try in order: env override, certifi, OS store."""
    contexts: list[ssl.SSLContext] = []
    override = os.environ.get("KYA_CA_BUNDLE", "").strip()
    if override and os.path.isfile(override):
        ctx = _ctx_from_cafile(override)
        if ctx is not None:
            contexts.append(ctx)
    try:
        import certifi
        ctx = _ctx_from_cafile(certifi.where())
        if ctx is not None:
            contexts.append(ctx)
    except Exception:
        pass
    contexts.append(ssl.create_default_context())
    return contexts


def connect_tls(host: str, port: int, timeout: float = 8.0) -> ssl.SSLSocket:
    """Open a verified TLS connection, retrying with the next CA source only on
    certificate-verification failures (a failed socket is never reused)."""
    last_exc: Exception | None = None
    for ctx in make_ssl_contexts():
        raw = socket.create_connection((host, port), timeout=timeout)
        try:
            return ctx.wrap_socket(raw, server_hostname=host)
        except ssl.SSLCertVerificationError as exc:
            last_exc = exc
            try:
                raw.close()
            except OSError:
                pass
        except Exception:
            try:
                raw.close()
            except OSError:
                pass
            raise
    assert last_exc is not None
    raise last_exc
