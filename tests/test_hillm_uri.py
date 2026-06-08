"""Tests for hillm:// URI layer via uri2hillm."""

from __future__ import annotations

import json
import subprocess

import pytest

from nlp2uri.compile import compile_uri_to_actions
from nlp2uri.cqrs import CqrsDispatcher
from nlp2uri.models import HostPlatform

uri2hillm = pytest.importorskip("uri2hillm")
hillm_uri = pytest.importorskip("uri2hillm.uri")
hillm_compile = pytest.importorskip("uri2hillm.compile")
hillm_run = pytest.importorskip("uri2hillm.run")


def test_is_hillm_uri() -> None:
    uri = hillm_uri.uri_for_cmd("READ", device="camera-usb", dry_run=True)
    assert uri == "hillm://cmd/READ?device=camera-usb&dry_run=true"
    assert hillm_uri.is_hillm_uri(uri)
    assert not hillm_uri.is_hillm_uri("getv://llm/groq/KEY")


def test_compile_hillm_uri_returns_os_action() -> None:
    uri = hillm_uri.uri_for_cmd("HEALTH")
    actions = hillm_compile.compile_hillm_uri(uri, HostPlatform.LINUX)
    assert len(actions) == 1
    assert actions[0].command.endswith("uri2hillm")
    assert actions[0].args == [uri]


def test_compile_uri_to_actions_routes_hillm() -> None:
    uri = hillm_uri.uri_for_cmd("READ", device="sensor-temp", dry_run=True)
    actions = compile_uri_to_actions(uri, HostPlatform.LINUX)
    assert actions[0].args[0] == uri


def test_cqrs_hillm_driver_compile() -> None:
    uri = hillm_uri.uri_for_cmd("DEVICES", category="serial")
    dispatcher = CqrsDispatcher(platform=HostPlatform.LINUX)
    result = dispatcher.compile_uri(uri, target="uri2hillm")
    assert result["ok"] is True
    assert result["actions"][0]["command"].endswith("uri2hillm")
    assert result["actions"][0]["args"][0] == uri


def test_run_uri_dispatches_dry_run_read() -> None:
    uri = hillm_uri.uri_for_cmd("READ", device="sensor-temp", dry_run=True)
    result = hillm_run.run_uri(uri)
    assert result.ok is True
    assert result.verb == "READ"
    payload = json.loads(result.output)
    assert payload["device_id"] == "sensor-temp"


def test_uri2hillm_cli_executes_via_subprocess() -> None:
    uri = hillm_uri.uri_for_cmd("HEALTH")
    proc = subprocess.run(
        ["uri2hillm", uri],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["verb"] == "HEALTH"
    assert payload["data"]["package"] == "hillm"


def test_nlp2uri_systemmap_wrapper_exports() -> None:
    from nlp2uri.systemmap import hillm_uri as wrapper

    assert wrapper.is_hillm_uri(hillm_uri.uri_for_cmd("HEALTH"))
    assert wrapper.compile_hillm_uri is not None
    assert wrapper.run_uri is not None
