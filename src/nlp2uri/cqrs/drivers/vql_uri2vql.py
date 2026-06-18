"""vql:// driver — uri2vql dispatch."""

from __future__ import annotations

from typing import Any

from nlp2uri.cqrs.base import CompileResult, UriDriver
from nlp2uri.models import HostPlatform


class VqlUri2vqlDriver(UriDriver):
    scheme = "vql"
    target = "uri2vql"

    def compile(
        self,
        uri: str,
        *,
        platform: HostPlatform,
        config: dict[str, Any] | None = None,
    ) -> CompileResult:
        del config
        try:
            from nlp2uri.systemmap.vql_uri import compile_vql_uri

            if compile_vql_uri is None:
                raise RuntimeError("uri2vql not installed: pip install uri2vql")
            actions = compile_vql_uri(uri, platform)
            return CompileResult(ok=True, uri=uri, actions=actions)
        except Exception as exc:
            return CompileResult(ok=False, uri=uri, error=str(exc))
