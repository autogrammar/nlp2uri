"""gillm:// driver — uri2gillm dispatch."""

from __future__ import annotations

from typing import Any

from nlp2uri.cqrs.base import CompileResult, UriDriver
from nlp2uri.models import HostPlatform


class GillmUri2gillmDriver(UriDriver):
    scheme = "gillm"
    target = "uri2gillm"

    def compile(
        self,
        uri: str,
        *,
        platform: HostPlatform,
        config: dict[str, Any] | None = None,
    ) -> CompileResult:
        del config
        try:
            from nlp2uri.systemmap.gillm_uri import compile_gillm_uri, is_gillm_uri

            if not is_gillm_uri(uri):
                raise ValueError(f"not a gillm uri: {uri}")
            actions = compile_gillm_uri(uri, platform)
            return CompileResult(ok=True, uri=uri, actions=actions)
        except Exception as exc:
            return CompileResult(ok=False, uri=uri, error=str(exc))
