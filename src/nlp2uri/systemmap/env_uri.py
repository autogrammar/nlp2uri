"""env:// URI layer — delegates to uri2env (nlp2env package)."""

from __future__ import annotations

from typing import Any

try:
    from uri2env.compile import compile_env_uri
    from uri2env.materialize import MaterializeResult, materialize_uri
    from uri2env.resolve import ResolvedEnvUri, resolve_prompt_to_env_uri
    from uri2env.uri import (
        ENV_SCHEME,
        build_env_uri_index,
        is_env_uri,
        parse_env_uri,
        uri_for_env_file,
        uri_for_getv_profile,
        uri_for_getv_var,
        uri_for_nlp2env_profile,
    )
except ImportError:
    compile_env_uri = None  # type: ignore
    materialize_uri = None  # type: ignore
    resolve_prompt_to_env_uri = None  # type: ignore
    is_env_uri = lambda uri: False  # type: ignore
    ENV_SCHEME = "env"

__all__ = [
    "ENV_SCHEME",
    "MaterializeResult",
    "ResolvedEnvUri",
    "build_env_uri_index",
    "compile_env_uri",
    "is_env_uri",
    "materialize_uri",
    "parse_env_uri",
    "resolve_prompt_to_env_uri",
    "uri_for_env_file",
    "uri_for_getv_profile",
    "uri_for_getv_var",
    "uri_for_nlp2env_profile",
]
