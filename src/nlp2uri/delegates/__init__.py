"""Optional delegation to *2llm adapter packages."""

from nlp2uri.delegates.llm_bridge import (
    dsl_to_gillm_uri,
    dsl_to_hillm_uri,
    dsl_to_tillm_uri,
    resolve_llm_prompt,
)

__all__ = [
    "dsl_to_gillm_uri",
    "dsl_to_hillm_uri",
    "dsl_to_tillm_uri",
    "resolve_llm_prompt",
]
