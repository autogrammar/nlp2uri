"""gillm:// URI layer — delegates to uri2gillm."""

from __future__ import annotations

from urllib.parse import urlparse

try:
    from uri2gillm.run import run_uri
    from uri2gillm.uri import GILLM_SCHEME, uri_for_cmd
except ImportError:
    run_uri = None  # type: ignore[assignment]
    uri_for_cmd = None  # type: ignore[assignment]
    GILLM_SCHEME = "gillm"


def is_gillm_uri(uri: str) -> bool:
    try:
        from uri2gillm.uri import is_gillm_uri as _is_gillm_uri

        return _is_gillm_uri(uri)
    except ImportError:
        return urlparse(uri).scheme.lower() == GILLM_SCHEME


def compile_gillm_uri(uri: str, host: object) -> list[object]:
    if not is_gillm_uri(uri):
        raise ValueError(f"not a gillm uri: {uri}")
    import shutil

    from nlp2uri.models import OSAction

    runner = shutil.which("uri2gillm") or "uri2gillm"
    return [OSAction(host, runner, [uri])]


__all__ = [
    "GILLM_SCHEME",
    "compile_gillm_uri",
    "is_gillm_uri",
    "run_uri",
    "uri_for_cmd",
]
