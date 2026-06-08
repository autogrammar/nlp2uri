"""tillm:// URI layer — delegates to uri2tillm."""

from __future__ import annotations

from urllib.parse import urlparse

try:
    from uri2tillm.run import run_uri
    from uri2tillm.uri import TILLM_SCHEME, uri_for_client, uri_for_cmd
except ImportError:
    run_uri = None  # type: ignore[assignment]
    uri_for_cmd = None  # type: ignore[assignment]
    uri_for_client = None  # type: ignore[assignment]
    TILLM_SCHEME = "tillm"


def is_tillm_uri(uri: str) -> bool:
    try:
        from uri2tillm.uri import is_tillm_uri as _is_tillm_uri

        return _is_tillm_uri(uri)
    except ImportError:
        return urlparse(uri).scheme.lower() == TILLM_SCHEME


def compile_tillm_uri(uri: str, host: object) -> list[object]:
    if not is_tillm_uri(uri):
        raise ValueError(f"not a tillm uri: {uri}")
    import shutil

    from nlp2uri.models import OSAction

    runner = shutil.which("uri2tillm") or "uri2tillm"
    return [OSAction(host, runner, [uri])]


__all__ = [
    "TILLM_SCHEME",
    "compile_tillm_uri",
    "is_tillm_uri",
    "run_uri",
    "uri_for_client",
    "uri_for_cmd",
]
