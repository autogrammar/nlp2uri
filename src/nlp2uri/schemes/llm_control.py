"""Build hillm://, gillm://, tillm:// UriSpec from delegated intents."""

from __future__ import annotations

from nlp2uri.models import UriIntent, UriSpec


def build_llm_control(intent: UriIntent, *, domain: str) -> UriSpec:
    uri = intent.params.get("uri") or intent.target
    if not uri.startswith(f"{domain}://"):
        raise ValueError(f"expected {domain}:// uri, got {uri!r}")
    return UriSpec(
        uri=uri,
        scheme=domain,
        action=f"{domain}_dispatch",
        platform_hints=(f"uri2{domain}", domain),
        metadata={"domain": domain, "delegated": True},
        intent=intent,
    )
