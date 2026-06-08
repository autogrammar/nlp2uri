"""hillm:// URI layer — delegates to uri2hillm (hillm package)."""

from __future__ import annotations

from typing import Any

try:
    from uri2hillm.compile import compile_hillm_uri
    from uri2hillm.run import run_uri
    from uri2hillm.uri import HILLM_SCHEME, is_hillm_uri, uri_for_cmd
except ImportError:
    compile_hillm_uri = None  # type: ignore[assignment]
    run_uri = None  # type: ignore[assignment]
    is_hillm_uri = lambda uri: False  # type: ignore[assignment,misc]
    HILLM_SCHEME = "hillm"
    uri_for_cmd = None  # type: ignore[assignment]

__all__ = [
    "HILLM_SCHEME",
    "compile_hillm_uri",
    "is_hillm_uri",
    "run_uri",
    "uri_for_cmd",
]
