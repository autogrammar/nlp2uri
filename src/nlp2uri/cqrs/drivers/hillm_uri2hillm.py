"""hillm:// driver — uri2hillm dispatch."""

from __future__ import annotations

from typing import Any

from nlp2uri.cqrs.base import CompileResult, UriDriver
from nlp2uri.models import HostPlatform


class HillmUri2hillmDriver(UriDriver):
    scheme = "hillm"
    target = "uri2hillm"

    def compile(
        self,
        uri: str,
        *,
        platform: HostPlatform,
        config: dict[str, Any] | None = None,
    ) -> CompileResult:
        del config
        try:
            from nlp2uri.systemmap.hillm_uri import compile_hillm_uri

            if compile_hillm_uri is None:
                raise RuntimeError("uri2hillm not installed: pip install uri2hillm")
            actions = compile_hillm_uri(uri, platform)
            return CompileResult(ok=True, uri=uri, actions=actions)
        except Exception as exc:
            return CompileResult(ok=False, uri=uri, error=str(exc))
