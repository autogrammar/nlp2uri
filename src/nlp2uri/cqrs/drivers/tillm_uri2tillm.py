"""tillm:// driver — uri2tillm dispatch."""

from __future__ import annotations

from typing import Any

from nlp2uri.cqrs.base import CompileResult, UriDriver
from nlp2uri.models import HostPlatform


class TillmUri2tillmDriver(UriDriver):
    scheme = "tillm"
    target = "uri2tillm"

    def compile(
        self,
        uri: str,
        *,
        platform: HostPlatform,
        config: dict[str, Any] | None = None,
    ) -> CompileResult:
        del config
        try:
            from nlp2uri.systemmap.tillm_uri import compile_tillm_uri, is_tillm_uri

            if not is_tillm_uri(uri):
                raise ValueError(f"not a tillm uri: {uri}")
            actions = compile_tillm_uri(uri, platform)
            return CompileResult(ok=True, uri=uri, actions=actions)
        except Exception as exc:
            return CompileResult(ok=False, uri=uri, error=str(exc))
