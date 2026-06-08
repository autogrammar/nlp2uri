"""env:// driver — uri2env materialize."""

from __future__ import annotations

from typing import Any

from nlp2uri.cqrs.base import CompileResult, UriDriver
from nlp2uri.models import HostPlatform


class EnvUri2envDriver(UriDriver):
    scheme = "env"
    target = "uri2env"

    def compile(
        self,
        uri: str,
        *,
        platform: HostPlatform,
        config: dict[str, Any] | None = None,
    ) -> CompileResult:
        try:
            from nlp2uri.systemmap.env_uri import compile_env_uri

            if compile_env_uri is None:
                raise RuntimeError("uri2env not installed: pip install nlp2env")
            actions = compile_env_uri(uri, platform)
            return CompileResult(ok=True, uri=uri, actions=actions)
        except Exception as exc:
            return CompileResult(ok=False, uri=uri, error=str(exc))
