"""hillm:// URI layer — delegates to uri2hillm (hillm package)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

try:
    from uri2hillm.compile import compile_hillm_uri
    from uri2hillm.run import run_uri
    from uri2hillm.uri import HILLM_SCHEME, uri_for_cmd
except ImportError:
    compile_hillm_uri = None  # type: ignore[assignment]
    run_uri = None  # type: ignore[assignment]
    uri_for_cmd = None  # type: ignore[assignment]
    HILLM_SCHEME = "hillm"


def is_hillm_uri(uri: str) -> bool:
    try:
        from uri2hillm.uri import is_hillm_uri as _is_hillm_uri

        return _is_hillm_uri(uri)
    except ImportError:
        return urlparse(uri).scheme.lower() == HILLM_SCHEME


def _compile_hillm_uri_local(uri: str, host: Any) -> list[Any]:
    import shutil

    from nlp2uri.models import OSAction

    runner = shutil.which("uri2hillm") or "uri2hillm"
    return [OSAction(host, runner, [uri])]


if compile_hillm_uri is None:
    compile_hillm_uri = _compile_hillm_uri_local  # type: ignore[assignment]

__all__ = [
    "HILLM_SCHEME",
    "compile_hillm_uri",
    "is_hillm_uri",
    "run_uri",
    "uri_for_cmd",
]
