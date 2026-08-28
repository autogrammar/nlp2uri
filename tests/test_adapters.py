"""Adapter layer tests."""

from __future__ import annotations

import io
import sys

from nlp2uri.adapters.base import AdapterRequest
from nlp2uri.adapters.cli import CliAdapter
from nlp2uri.adapters.mcp import MCP_TOOLS, McpAdapter
from nlp2uri.adapters.rest import RestAdapter
from nlp2uri.adapters.shell import ShellAdapter
from nlp2uri.integrators.mcp_server import handle_message, run_stdio
from nlp2uri.models import HostPlatform


def test_cli_adapter_plan():
    response = CliAdapter().handle(
        AdapterRequest(operation="plan", prompt="open firefox", platform=HostPlatform.LINUX)
    )
    assert response.ok
    assert response.data["uri"].startswith("app://firefox/open")


def test_rest_adapter_plan():
    response = RestAdapter().dispatch(
        "plan",
        {"prompt": "open firefox", "platform": "linux"},
    )
    assert response.ok
    assert "uri" in response.data


def test_shell_adapter_export():
    response = ShellAdapter().handle(
        AdapterRequest(operation="export", prompt="open firefox", platform=HostPlatform.LINUX)
    )
    assert response.ok
    assert "NLP2URI_URI=" in response.data["script"]
    assert "app://firefox/open" in response.data["script"]


def test_mcp_adapter_tools():
    adapter = McpAdapter()
    response = adapter.call_tool(
        "nlp2uri_plan",
        {"prompt": "capture screen", "platform": "linux"},
    )
    assert response.ok
    assert response.data["uri"].startswith("desktop-screenshot://")
    assert response.data["mcp_content"]


def test_mcp_execute_defaults_to_dry_run(monkeypatch):
    monkeypatch.delenv("NLP2URI_MCP_ALLOW_EXECUTE", raising=False)
    schema = next(tool for tool in MCP_TOOLS if tool["name"] == "nlp2uri_execute")
    assert schema["inputSchema"]["properties"]["dry_run"]["default"] is True

    observed: list[bool | None] = []
    adapter = McpAdapter()

    def fake_handle_uri(uri, *, dry_run=None, text=None):
        observed.append(dry_run)
        return {"uri": uri, "actions": [], "result": {"ok": True}}

    monkeypatch.setattr(adapter.service, "handle_uri", fake_handle_uri)
    response = adapter.call_tool("nlp2uri_execute", {"uri": "app://firefox/open"})
    assert response.ok
    assert observed == [True]


def test_mcp_execute_rejects_live_action_without_server_permission(monkeypatch):
    monkeypatch.delenv("NLP2URI_MCP_ALLOW_EXECUTE", raising=False)
    response = McpAdapter().call_tool(
        "nlp2uri_execute",
        {"uri": "app://firefox/open", "dry_run": False},
    )
    assert response.ok is False
    assert response.status_code == 403
    assert "NLP2URI_MCP_ALLOW_EXECUTE" in response.error


def test_mcp_stdio_initialize():
    adapter = McpAdapter()
    msg = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    out = handle_message(msg, adapter=adapter)
    assert out is not None
    assert out["result"]["serverInfo"]["name"] == "nlp2uri"


def test_mcp_list_system_uris_inline_map():
    adapter = McpAdapter()
    response = adapter.call_tool(
        "nlp2uri_list_system_uris",
        {
            "system_map": {
                "format": "nlp2dsl.system_map.v1",
                "example_id": "demo",
                "commands": [{"name": "ping", "runtime": "executor:worker"}],
                "runtimes": [{"id": "executor:worker", "kind": "worker"}],
            },
            "limit": 1,
        },
    )
    assert response.ok
    assert response.data["count"] >= 2
    assert response.data["returned_count"] == 1
    assert response.data["truncated"] is True


def test_mcp_resolve_system_map_with_fallback():
    adapter = McpAdapter()
    response = adapter.call_tool(
        "nlp2uri_resolve_system_map",
        {
            "prompt": "send invoice",
            "platform": "linux",
            "system_map": {
                "format": "nlp2dsl.system_map.v1",
                "example_id": "01-invoice",
                "commands": [
                    {
                        "name": "send_invoice",
                        "runtime": "executor:worker",
                        "fields": [{"name": "amount"}, {"name": "to"}],
                    }
                ],
                "runtimes": [{"id": "executor:worker", "kind": "worker"}],
            },
        },
    )
    assert response.ok
    assert response.data["source"] == "system_map"
    assert "send_invoice" in response.data["uri"]


def test_mcp_stdio_tools_call():
    adapter = McpAdapter()
    msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "nlp2uri_resolve",
            "arguments": {"prompt": "open firefox", "platform": "linux"},
        },
    }
    out = handle_message(msg, adapter=adapter)
    assert out is not None
    text = out["result"]["content"][0]["text"]
    assert "app://firefox/open" in text or "firefox" in text


def test_mcp_error_response_does_not_expose_traceback():
    class BrokenAdapter:
        def call_tool(self, _name, _arguments):
            raise RuntimeError("boom")

    msg = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": "broken", "arguments": {}},
    }
    out = handle_message(msg, adapter=BrokenAdapter())
    text = out["result"]["content"][0]["text"]
    assert "RuntimeError: boom" in text
    assert "Traceback" not in text


def test_mcp_startup_does_not_create_config(tmp_path, monkeypatch):
    from nlp2uri.config import reset_config_cache

    config_path = tmp_path / "nlp2uri.yaml"
    config_path.unlink()
    monkeypatch.delenv("NLP2URI_CONFIG")
    reset_config_cache()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))

    assert run_stdio(adapter=McpAdapter()) == 0
    assert not config_path.exists()
