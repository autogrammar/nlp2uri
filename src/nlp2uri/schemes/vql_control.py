"""Build vql:// UriSpec from delegated intents."""

from __future__ import annotations

from nlp2uri.models import UriIntent, UriSpec


def build_vql_control(intent: UriIntent) -> UriSpec:
    uri = intent.params.get("uri") or intent.target
    dsl = intent.params.get("dsl")
    mode = intent.params.get("mode", "uri")
    if mode == "dsl" and dsl:
        return UriSpec(
            uri=f"vql://dsl?line={dsl}",
            scheme="vql",
            action="vql_dsl_dispatch",
            platform_hints=("dsl2vql", "vql"),
            metadata={"domain": "vql", "delegated": True, "mode": "dsl", "dsl": dsl},
            intent=intent,
        )
    if not uri.startswith("vql://"):
        raise ValueError(f"expected vql:// uri, got {uri!r}")
    return UriSpec(
        uri=uri,
        scheme="vql",
        action="vql_dispatch",
        platform_hints=("uri2vql", "vql"),
        metadata={"domain": "vql", "delegated": True, "mode": "uri"},
        intent=intent,
    )
