"""Unit tests for NL -> DSL -> LLM intent compiler (STARTER-022)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from nlp2uri.llm_intent import (
    URI_INTENT_EBNF,
    compile_nl_to_intent_llm,
    parse_intent_grammar_fallback,
)
from nlp2uri.models import IntentKind
from nlp2uri.parse_nl import parse_text


def test_ebnf_grammar_defined() -> None:
    assert "UriIntent" in URI_INTENT_EBNF
    assert "Kind" in URI_INTENT_EBNF


def test_grammar_fallback_hardware() -> None:
    intent = parse_intent_grammar_fallback("sprawdź stan myszki na porcie")
    assert intent is not None
    assert intent.kind == IntentKind.HILLM
    assert "mouse" in intent.target


def test_grammar_fallback_terminal_agent() -> None:
    intent = parse_intent_grammar_fallback("uruchom aider z zadaniem refaktoryzacji")
    assert intent is not None
    assert intent.kind == IntentKind.TILLM
    assert "aider" in intent.target


def test_grammar_fallback_navigate() -> None:
    intent = parse_intent_grammar_fallback("subactor.com")
    assert intent is not None
    assert intent.kind == IntentKind.NAVIGATE
    assert intent.target == "https://subactor.com"


def test_compile_nl_to_intent_llm_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NLP2URI_FORCE_LLM", "1")
    fake_json = {
        "kind": "capture",
        "target": "window",
        "params": {"title": "Terminal", "mode": "active"},
        "confidence": 0.95,
    }
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content=json.dumps(fake_json)))]
    mock_litellm = MagicMock()
    mock_litellm.completion.return_value = mock_resp

    with patch.dict("sys.modules", {"litellm": mock_litellm}):
        intent = compile_nl_to_intent_llm("zrób zrzut aktywnego okna konsoli")
        assert intent is not None
        assert intent.kind == IntentKind.CAPTURE
        assert intent.target == "window"
        assert intent.params.get("title") == "Terminal"
        assert intent.confidence == 0.95


@patch("nlp2uri.llm_intent.compile_nl_to_intent_llm")
def test_parse_text_uses_llm_fallback(mock_llm: MagicMock) -> None:
    from nlp2uri.models import UriIntent

    mock_llm.return_value = UriIntent(
        kind=IntentKind.OPEN,
        target="app",
        params={"name": "custom-ide"},
        raw_text="odpal nietypowe ide",
        confidence=0.9,
    )

    intent = parse_text("odpal nietypowe ide")
    assert intent.kind == IntentKind.OPEN
    assert intent.params.get("name") == "custom-ide"
