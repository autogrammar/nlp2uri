"""Structured NL -> DSL -> LLM intent compiler for UriIntent.

Eliminates hardcoded regex heuristics by providing a formal EBNF grammar
and a structured JSON extraction schema supported by LiteLLM / local models.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from nlp2uri.models import IntentKind, UriIntent

URI_INTENT_EBNF = """
UriIntent       ::= Kind Target Params?
Kind            ::= 'open' | 'capture' | 'focus' | 'move' | 'navigate'
                  | 'ide_open' | 'ide_chat_send' | 'ide_command' | 'ide_status'
                  | 'hillm' | 'gillm' | 'tillm' | 'vql'
Target          ::= AppTarget | FileTarget | SettingsTarget | TerminalTarget | UriTarget
AppTarget       ::= 'app'
FileTarget      ::= 'file'
SettingsTarget  ::= 'settings'
TerminalTarget  ::= 'terminal'
UriTarget       ::= Scheme '://' Path
Params          ::= '{' (Param (',' Param)*)? '}'
Param           ::= Key ':' Value
"""

INTENT_EXTRACTION_SYSTEM_PROMPT = """You are a natural language compiler for the nlp2uri system.
Your job is to parse natural language instructions (English or Polish) into a structured UriIntent.

Possible Intent Kinds:
- open: open an application (target='app', params={'name': '<app_name>'}), file (target='file', params={'path': '<path>'}), terminal (target='terminal', params={'path': '<opt_path>'}), or settings (target='settings', params={'panel': '<opt_panel>'})
- capture: take a screenshot (target='screen' or 'window', params={'title': '<opt_title>', 'mode': 'active' | 'fullscreen'})
- focus: bring a window to front (target='window', params={'name': '<app_name>'})
- move: move a window between monitors/screens (target='window', params={'title': '<title>', 'screen': '<screen_num>'})
- navigate: open a web URL in a browser (target='<url>', params={})
- ide_open: open an IDE with a project (target='cursor'|'vscode', params={'path': '<path>'})
- ide_chat_send: send message to IDE chat (target='cursor'|'vscode', params={'text': '<msg>'})
- ide_command: run IDE palette command (target='cursor'|'vscode', params={'command': '<cmd>'})
- ide_status: check IDE plugin status (target='cursor'|'vscode', params={})
- hillm: hardware inspection / sensors / usb / mouse / keyboard (target='hillm://cmd/<VERB>?<params>')
- gillm: GUI automation / workflow (target='gillm://cmd/<VERB>?<params>')
- tillm: terminal / agent CLI (e.g. aider, claude, codex) (target='tillm://client/<client>?prompt=<prompt>')
- vql: visual query language (target='vql://...')

Respond ONLY with a JSON object matching this schema:
{
  "kind": "<kind>",
  "target": "<target>",
  "params": { ... },
  "confidence": 0.0 - 1.0
}
"""


def compile_nl_to_intent_llm(
    prompt: str,
    *,
    model: str | None = None,
    timeout: float = 10.0,
) -> UriIntent | None:
    """Uses LiteLLM to compile natural language prompt into UriIntent."""
    text = (prompt or "").strip()
    if not text:
        return None

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key and not os.getenv("NLP2URI_FORCE_LLM"):
        return None

    try:
        import litellm

        target_model = model or os.getenv("NLP2URI_LLM_MODEL", "gpt-4o-mini")
        messages = [
            {"role": "system", "content": INTENT_EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Parse this natural language instruction: {text!r}"},
        ]
        response = litellm.completion(
            model=target_model,
            messages=messages,
            response_format={"type": "json_object"},
            timeout=timeout,
            temperature=0.0,
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        kind_str = data.get("kind", "").lower()
        if kind_str not in IntentKind.__members__.values() and kind_str in [k.value for k in IntentKind]:
            kind = IntentKind(kind_str)
        else:
            kind = IntentKind[kind_str.upper()]
        return UriIntent(
            kind=kind,
            target=str(data.get("target", "")),
            params={str(k): str(v) for k, v in data.get("params", {}).items()},
            raw_text=text,
            confidence=float(data.get("confidence", 0.9)),
        )
    except Exception:
        return None


def parse_intent_grammar_fallback(prompt: str) -> UriIntent | None:
    """Grammar-based structured tokenizer fallback when LLM is unavailable."""
    text = (prompt or "").strip()
    if not text:
        return None
    lower = text.lower()

    # Hardware / sensors -> hillm
    if any(k in lower for k in ("mysz", "myszka", "mouse", "klawiatur", "keyboard", "czujnik", "sensor", "temperat", "usb")):
        from nlp2uri.delegates.llm_bridge import prompt_to_hillm_uri
        uri = prompt_to_hillm_uri(text)
        if uri:
            return UriIntent(kind=IntentKind.HILLM, target=uri, params={"uri": uri, "domain": "hillm"}, raw_text=text, confidence=0.85)

    # Terminal CLI agents -> tillm
    if any(k in lower for k in ("aider", "claude", "codex", "gemini", "devin", "tillm")):
        from nlp2uri.delegates.llm_bridge import prompt_to_tillm_uri
        uri = prompt_to_tillm_uri(text)
        if uri:
            return UriIntent(kind=IntentKind.TILLM, target=uri, params={"uri": uri, "domain": "tillm"}, raw_text=text, confidence=0.85)

    # Browser navigation
    if lower.startswith(("http://", "https://", "www.")) or re.match(r"^[\w.-]+\.(com|org|net|pl|io|dev|edu)(?:/|\?|$)", lower):
        target = text if text.startswith(("http://", "https://")) else f"https://{text}"
        return UriIntent(kind=IntentKind.NAVIGATE, target=target, params={}, raw_text=text, confidence=0.9)

    return None
