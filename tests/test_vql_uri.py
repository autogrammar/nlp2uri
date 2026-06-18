"""Tests for vql:// URI layer via uri2vql."""

from __future__ import annotations

import json
import subprocess

import pytest

from nlp2uri.compile import compile_uri_to_actions
from nlp2uri.cqrs import CqrsDispatcher
from nlp2uri.models import HostPlatform

uri2vql = pytest.importorskip("uri2vql")
vql_uri = pytest.importorskip("uri2vql.uri")
vql_compile = pytest.importorskip("uri2vql.compile")
vql_run = pytest.importorskip("uri2vql.run")


def test_is_vql_uri() -> None:
    uri = vql_uri.uri_for_window_summary("app.vql.json")
    assert uri == "vql://window/summary?file=app.vql.json"
    assert vql_uri.is_vql_uri(uri)
    assert not vql_uri.is_vql_uri("hillm://cmd/HEALTH")


def test_compile_vql_uri_returns_os_action() -> None:
    uri = vql_uri.uri_for_program("app.vql.json")
    actions = vql_compile.compile_vql_uri(uri, HostPlatform.LINUX)
    assert len(actions) == 1
    assert actions[0].command.endswith("uri2vql")
    assert actions[0].args == ["run", "--uri", uri]


def test_compile_uri_to_actions_routes_vql() -> None:
    uri = vql_uri.uri_for_window_analyze(file="screen.vql.json", grid=8)
    actions = compile_uri_to_actions(uri, HostPlatform.LINUX)
    assert actions[0].args[2] == uri


def test_cqrs_vql_driver_compile() -> None:
    uri = vql_uri.uri_for_objects("app.vql.json")
    dispatcher = CqrsDispatcher(platform=HostPlatform.LINUX)
    result = dispatcher.compile_uri(uri, target="uri2vql")
    assert result["ok"] is True
    assert result["actions"][0]["command"].endswith("uri2vql")
    assert result["actions"][0]["args"][2] == uri


def test_nlp2uri_systemmap_wrapper_exports() -> None:
    from nlp2uri.systemmap import vql_uri as wrapper

    assert wrapper.is_vql_uri(vql_uri.uri_for_program())
    assert wrapper.compile_vql_uri is not None


def test_uri2vql_cli_resolve() -> None:
    proc = subprocess.run(
        ["uri2vql", "resolve", "opisz ekran vql", "--file", "app.vql.json"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload[0]["uri"].startswith("vql://window/summary")


def test_compile_vql_without_uri2vql_package() -> None:
    uri = "vql://program?file=app.vql.json"
    actions = compile_uri_to_actions(uri, HostPlatform.LINUX)
    assert len(actions) == 1
    assert actions[0].args[0] == "run"
    assert actions[0].args[2] == uri
