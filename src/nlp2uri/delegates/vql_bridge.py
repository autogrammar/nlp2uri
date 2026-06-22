"""NL → vql:// URI delegation."""

from __future__ import annotations

import re

# The vql domain is only entered when the prompt explicitly names it (``vql`` or
# ``vector``). Action words like ``screenshot``/``capture``/``draw``/``describe``
# decide *which* vql URI is built (see ``_fallback_prompt_to_vql_uri`` / ``best_uri``),
# but on their own they are plain desktop intents (screenshot, draw, …) and must not
# be hijacked into vql — otherwise "capture screen" resolves to vql://window/analyze
# instead of desktop-screenshot://.
_VQL_RE = re.compile(r"\b(vql|vector)\b", re.IGNORECASE)


def prompt_to_vql_uri(prompt: str, *, file: str | None = None) -> str | None:
    text = prompt.strip()
    if not text or not _VQL_RE.search(text):
        return None
    try:
        from uri2vql.nlp2uri import best_uri

        hit = best_uri(text, file=file)
        return hit.uri if hit else None
    except ImportError:
        return _fallback_prompt_to_vql_uri(text, file=file)


def prompt_to_vql_dsl(prompt: str, *, file: str | None = None) -> str | None:
    text = prompt.strip()
    if not text or not _VQL_RE.search(text):
        return None
    try:
        from nlp2vql.to_dsl import to_dsl

        return to_dsl(text, file=file)
    except ImportError:
        return None


_GENERATE_WORDS = (
    "narysuj",
    "draw",
    "compile",
    "skompiluj",
    "validate",
    "waliduj",
    "render",
    "wygeneruj",
    "generate",
    "stwórz",
    "stworz",
)


def resolve_vql_prompt(prompt: str, *, file: str | None = None) -> tuple[str, str] | None:
    """Return (mode, payload) where mode is 'uri' or 'dsl'."""
    lowered = prompt.lower()
    if any(word in lowered for word in _GENERATE_WORDS):
        dsl = prompt_to_vql_dsl(prompt, file=file)
        if dsl:
            return "dsl", dsl

    uri = prompt_to_vql_uri(prompt, file=file)
    if uri:
        return "uri", uri
    return None


def _fallback_prompt_to_vql_uri(prompt: str, *, file: str | None = None) -> str | None:
    lowered = prompt.lower()
    out_file = file or "app.vql.json"
    if any(h in lowered for h in ("zrzut", "screenshot", "capture", "przechwyć", "przechwyc")):
        return f"vql://window/analyze?file={out_file}&monitor=1&grid=12"
    if any(h in lowered for h in ("opisz", "opis", "describe", "summary", "podsumowanie")):
        return f"vql://window/summary?file={out_file}"
    if any(h in lowered for h in ("obiekty", "objects")):
        return f"vql://objects?file={out_file}"
    if any(h in lowered for h in ("scena", "scene")):
        return f"vql://scene?file={out_file}"
    if "vql" in lowered or "vector" in lowered:
        return f"vql://program?file={out_file}"
    return None
