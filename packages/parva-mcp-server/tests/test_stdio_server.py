from __future__ import annotations

import json
import subprocess
import sys

from parva_mcp_server.manifest import PROMPTS, RESOURCES, TOOLS
from parva_mcp_server.server import handle_jsonrpc_request


def _request(method: str, params: dict | None = None, request_id: int = 1) -> dict:
    response = handle_jsonrpc_request(
        {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
    )
    assert response is not None
    return response


def test_initialize_response() -> None:
    response = _request("initialize", {"protocolVersion": "2024-11-05"})
    assert response["result"]["serverInfo"]["name"] == "parva-mcp-server"
    assert "tools" in response["result"]["capabilities"]


def test_tools_list_returns_exact_safe_tools() -> None:
    response = _request("tools/list")
    names = {tool["name"] for tool in response["result"]["tools"]}
    assert names == {tool["name"] for tool in TOOLS}
    assert all(tool["not_authority"] is True for tool in response["result"]["tools"])


def test_resources_list_returns_exact_safe_resources() -> None:
    response = _request("resources/list")
    uris = {resource["uri"] for resource in response["result"]["resources"]}
    assert uris == set(RESOURCES)


def test_prompts_list_returns_exact_safe_prompts() -> None:
    response = _request("prompts/list")
    names = {prompt["name"] for prompt in response["result"]["prompts"]}
    assert names == set(PROMPTS)


def test_prompts_get_preserves_safety_boundary() -> None:
    response = _request("prompts/get", {"name": "check_claim_with_sources"})
    text = response["result"]["messages"][0]["content"]["text"]
    assert "claim_boundary" in text
    assert "review_required" in text
    assert "not_authority" in text


def test_tools_call_convert_ad_to_bs_returns_boundaries() -> None:
    response = _request("tools/call", {"name": "convert_ad_to_bs", "arguments": {"date": "2026-04-14"}})
    content = response["result"]["structuredContent"]
    assert content["status"] == "manifest_only"
    assert content["route"] == "/v3/api/calendar/convert"
    assert content["claim_boundary"] == "decision_support_not_authority"
    assert content["review_required"] is True
    assert content["not_authority"] is True


def test_unknown_tool_returns_jsonrpc_error() -> None:
    response = _request("tools/call", {"name": "future_bs_exact_prediction", "arguments": {}})
    assert response["error"]["code"] == -32602
    assert "Unknown" in response["error"]["message"]


def test_private_route_cannot_be_called() -> None:
    response = _request("tools/call", {"name": "loan-impact", "arguments": {}})
    assert response["error"]["code"] == -32602


def test_resources_read_rejects_arbitrary_file_paths() -> None:
    response = _request("resources/read", {"uri": "../../README.md"})
    assert response["error"]["code"] == -32602
    assert "parva://" in response["error"]["message"]


def test_resources_read_rejects_file_scheme() -> None:
    response = _request("resources/read", {"uri": "file:///etc/passwd"})
    assert response["error"]["code"] == -32602
    assert "parva://" in response["error"]["message"]


def test_resources_read_safe_resource() -> None:
    response = _request("resources/read", {"uri": "parva://benchmark-summary"})
    text = response["result"]["contents"][0]["text"]
    payload = json.loads(text)
    assert payload["claim_boundary"] == "technical_benchmark_not_authority"
    assert payload["not_authority"] is True


def test_manifest_cli_still_works() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "parva_mcp_server.server", "--manifest"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["name"] == "parva-public-temporal-tools"


def test_check_cli_still_works() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "parva_mcp_server.server", "--check"],
        text=True,
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert json.loads(proc.stdout)["ok"] is True


def test_stdio_handles_jsonrpc_line_and_stdout_is_json_only() -> None:
    request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/list",
        "params": {},
    }
    proc = subprocess.run(
        [sys.executable, "-m", "parva_mcp_server.server", "--stdio"],
        input=json.dumps(request) + "\n",
        text=True,
        capture_output=True,
        check=False,
        timeout=5,
    )
    assert proc.returncode == 0
    assert proc.stderr == ""
    lines = proc.stdout.splitlines()
    assert len(lines) == 1
    response = json.loads(lines[0])
    assert response["id"] == 7
    assert "tools" in response["result"]


def test_stdio_process_stays_alive_until_stdin_closes() -> None:
    proc = subprocess.Popen(
        [sys.executable, "-m", "parva_mcp_server.server", "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None
    proc.stdin.write('{"jsonrpc":"2.0","id":8,"method":"initialize","params":{}}\n')
    proc.stdin.flush()
    response = json.loads(proc.stdout.readline())
    assert response["id"] == 8
    assert proc.poll() is None
    proc.stdin.close()
    proc.wait(timeout=5)
    assert proc.returncode == 0
    assert proc.stderr is not None
    assert proc.stderr.read() == ""
