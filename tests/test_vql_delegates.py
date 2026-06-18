"""Tests for VQL NL delegation in nlp2uri."""

from __future__ import annotations

import pytest

from nlp2uri import compile_uri_to_actions, nlp2uri
from nlp2uri.delegates.vql_bridge import prompt_to_vql_uri, resolve_vql_prompt
from nlp2uri.models import HostPlatform, IntentKind
from nlp2uri.parse_nl import parse_text

pytest.importorskip("uri2vql")


def test_screenshot_vql_prompt_routes_to_analyze() -> None:
    prompt = "zrób zrzut ekranu vql"
    intent = parse_text(prompt)
    assert intent.kind == IntentKind.VQL
    assert intent.target.startswith("vql://window/analyze")
    assert "file=app.vql.json" in intent.target


def test_describe_screen_vql_prompt_routes_to_summary() -> None:
    prompt = "opisz ekran vql"
    intent = parse_text(prompt)
    assert intent.kind == IntentKind.VQL
    assert intent.target.startswith("vql://window/summary")


def test_absolute_vql_uri_parsed() -> None:
    uri = "vql://objects?file=screen.vql.json"
    intent = parse_text(uri)
    assert intent.kind == IntentKind.VQL
    assert intent.target == uri


def test_prompt_to_vql_uri_objects() -> None:
    uri = prompt_to_vql_uri("pokaż obiekty vql", file="screen.vql.json")
    assert uri is not None
    assert uri.startswith("vql://objects")


def test_resolve_vql_prompt_priority() -> None:
    hit = resolve_vql_prompt("przechwyć ekran i opisz vql")
    assert hit is not None
    assert hit[0] == "uri"
    assert hit[1].startswith("vql://window/summary")


def test_nlp2uri_plan_vql_screenshot() -> None:
    prompt = "zrób zrzut ekranu vql"
    plan = nlp2uri(prompt, os=HostPlatform.LINUX)
    assert plan.uri.startswith("vql://window/analyze")
    assert plan.intent == "vql_control"
    assert plan.actions[0].command.endswith("uri2vql")
    assert plan.actions[0].args[2] == plan.uri


def test_compile_vql_dsl_mode() -> None:
    prompt = "narysuj czerwone koło vql"
    intent = parse_text(prompt)
    assert intent.kind == IntentKind.VQL
    actions = compile_uri_to_actions(intent.target, HostPlatform.LINUX)
    assert actions[0].command.endswith("dsl2vql")
    assert "GENERATE" in actions[0].args[1] or "COMPILE" in actions[0].args[1]
