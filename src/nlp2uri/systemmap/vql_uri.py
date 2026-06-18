"""vql:// URI layer — delegates to uri2vql (vql package)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

try:
    from uri2vql.compile import compile_vql_uri
    from uri2vql.run import run_uri
    from uri2vql.uri import VQL_SCHEME, is_vql_uri
except ImportError:
    compile_vql_uri = None  # type: ignore[assignment]
    run_uri = None  # type: ignore[assignment]
    is_vql_uri = None  # type: ignore[assignment]
    VQL_SCHEME = "vql"


def _is_vql_uri_local(uri: str) -> bool:
    return urlparse(uri).scheme.lower() == VQL_SCHEME


if is_vql_uri is None:
    is_vql_uri = _is_vql_uri_local  # type: ignore[assignment]


def _compile_vql_uri_local(uri: str, host: Any, *, dsl: str | None = None) -> list[Any]:
    import shutil
    from urllib.parse import parse_qs, unquote, urlparse

    from nlp2uri.models import OSAction

    dsl_line = dsl
    if not dsl_line:
        parsed = urlparse(uri)
        if (parsed.netloc + parsed.path).strip("/") == "dsl":
            dsl_line = unquote((parse_qs(parsed.query).get("line") or [""])[0]) or None

    if dsl_line:
        runner = shutil.which("dsl2vql") or "dsl2vql"
        return [OSAction(host, runner, ["-c", dsl_line, "--json"])]

    runner = shutil.which("uri2vql") or "uri2vql"
    return [OSAction(host, runner, ["run", "--uri", uri])]


if compile_vql_uri is None:
    compile_vql_uri = _compile_vql_uri_local  # type: ignore[assignment]


__all__ = [
    "VQL_SCHEME",
    "compile_vql_uri",
    "is_vql_uri",
    "run_uri",
]
