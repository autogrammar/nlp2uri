"""Tests for hillm/gillm/tillm NL delegation in nlp2uri."""

from __future__ import annotations

import pytest

from nlp2uri import compile_uri_to_actions, nlp2uri
from nlp2uri.delegates.llm_bridge import (
    prompt_to_gillm_uri,
    prompt_to_hillm_uri,
    prompt_to_tillm_uri,
    resolve_llm_prompt,
)
from nlp2uri.models import HostPlatform, IntentKind
from nlp2uri.parse_nl import parse_text


def test_mouse_port_question_routes_to_hillm() -> None:
    prompt = "na jakim porcie jest podłączona myszka?"
    intent = parse_text(prompt)
    assert intent.kind == IntentKind.HILLM
    assert intent.target.startswith("hillm://cmd/STATUS")
    assert "mouse-default" in intent.target
    assert "dry_run=true" in intent.target


def test_mouse_port_nlp2uri_plan() -> None:
    prompt = "na jakim porcie jest podłączona myszka?"
    plan = nlp2uri(prompt, os=HostPlatform.LINUX)
    assert plan.uri.startswith("hillm://")
    assert plan.intent == "hillm_control"
    assert plan.actions[0].command.endswith("uri2hillm")
    assert plan.actions[0].args[0] == plan.uri


def test_absolute_hillm_uri_parsed() -> None:
    uri = "hillm://cmd/HEALTH"
    intent = parse_text(uri)
    assert intent.kind == IntentKind.HILLM
    assert intent.target == uri


def test_gillm_health_prompt() -> None:
    uri = prompt_to_gillm_uri("gillm health check")
    assert uri == "gillm://cmd/HEALTH"


def test_tillm_aider_prompt() -> None:
    uri = prompt_to_tillm_uri("aider: add unit test for registry")
    assert uri is not None
    assert uri.startswith("tillm://")


def test_resolve_llm_prompt_priority() -> None:
    hit = resolve_llm_prompt("read temperature from usb sensor")
    assert hit is not None
    assert hit[0] == "hillm"


def test_compile_hillm_uri_without_uri2hillm_package() -> None:
    actions = compile_uri_to_actions(
        "hillm://cmd/STATUS?device=mouse-default&dry_run=true",
        HostPlatform.LINUX,
    )
    assert len(actions) == 1
    assert actions[0].args[0].startswith("hillm://")


@pytest.mark.skipif(
    not __import__("importlib").util.find_spec("uri2hillm"),
    reason="uri2hillm not installed",
)
def test_execute_hillm_mouse_status_dry_run() -> None:
    from nlp2uri.runtime import execute_uri

    plan = nlp2uri("na jakim porcie jest podłączona myszka?", os=HostPlatform.LINUX)
    result = execute_uri(plan.uri, platform=HostPlatform.LINUX, dry_run=False)
    assert result.ok, result.error or result.output
    assert "mouse" in (result.output or "").lower() or "input" in (result.output or "").lower()
