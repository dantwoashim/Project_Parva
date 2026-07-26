from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any

import anyio
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from parva_mcp_server.manifest import PROMPTS, RESOURCES, TOOLS

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _server_environment(origin: str) -> dict[str, str]:
    env = os.environ.copy()
    env["PARVA_PUBLIC_ORIGIN"] = origin
    env["PARVA_HTTP_TIMEOUT_SECONDS"] = "10"
    return env


async def _official_client_scenario(origin: str) -> dict[str, Any]:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "parva_mcp_server.server", "--stdio"],
        env=_server_environment(origin),
        cwd=PROJECT_ROOT,
    )
    with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stderr:
        async with stdio_client(parameters, errlog=stderr) as (read_stream, write_stream):
            async with ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=15),
            ) as session:
                initialized = await session.initialize()
                await session.send_ping()
                tools = await session.list_tools()
                resources = await session.list_resources()
                prompts = await session.list_prompts()
                conversion = await session.call_tool(
                    "convert_ad_to_bs",
                    {"date": "2026-04-14"},
                )
                benchmark = await session.read_resource("parva://benchmark-summary")
                invalid = await session.call_tool(
                    "convert_ad_to_bs",
                    {"date": "9999-01-01"},
                )
        stderr.seek(0)
        stderr_text = stderr.read()
    return {
        "initialized": initialized,
        "tools": tools,
        "resources": resources,
        "prompts": prompts,
        "conversion": conversion,
        "benchmark": benchmark,
        "invalid": invalid,
        "stderr": stderr_text,
    }


def test_official_client_initializes_discovers_and_executes(parva_http_stub: dict[str, Any]) -> None:
    result = anyio.run(_official_client_scenario, parva_http_stub["origin"])

    assert result["initialized"].serverInfo.name == "parva-mcp-server"
    assert result["initialized"].protocolVersion
    assert {tool.name for tool in result["tools"].tools} == {
        tool["name"] for tool in TOOLS
    }
    assert {str(resource.uri) for resource in result["resources"].resources} == set(RESOURCES)
    assert {prompt.name for prompt in result["prompts"].prompts} == set(PROMPTS)

    descriptors = {tool.name: tool for tool in result["tools"].tools}
    conversion_schema = descriptors["convert_ad_to_bs"].inputSchema
    assert conversion_schema["required"] == ["date"]
    assert conversion_schema["additionalProperties"] is False
    assert conversion_schema["properties"]["date"]["format"] == "date"

    conversion = result["conversion"]
    assert conversion.isError is False
    assert conversion.structuredContent["result"]["bikram_sambat"] == {
        "year": 2083,
        "month": 1,
        "day": 1,
        "month_name": "Baishakh",
    }
    assert conversion.structuredContent["not_authority"] is True
    assert conversion.structuredContent["review_required"] is False

    benchmark_text = result["benchmark"].contents[0].text
    assert json.loads(benchmark_text)["result"]["task_count"] == 64

    invalid = result["invalid"]
    assert invalid.isError is True
    assert invalid.structuredContent["error"]["code"] == "UNSUPPORTED_DATE_RANGE"
    assert invalid.structuredContent["review_required"] is True

    assert result["stderr"] == ""
    calls = parva_http_stub["calls"]
    assert all(call["path"] == "/v3/api/agent/run-tool" for call in calls)
    assert calls[0]["request"] == {
        "tool_name": "parva.convert_date",
        "input": {"ad_date": "2026-04-14"},
    }


def test_sdk_returns_schema_error_without_calling_http(parva_http_stub: dict[str, Any]) -> None:
    async def scenario() -> Any:
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "parva_mcp_server.server", "--stdio"],
            env=_server_environment(parva_http_stub["origin"]),
            cwd=PROJECT_ROOT,
        )
        with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stderr:
            async with stdio_client(parameters, errlog=stderr) as streams:
                async with ClientSession(
                    *streams,
                    read_timeout_seconds=timedelta(seconds=10),
                ) as session:
                    await session.initialize()
                    return await session.call_tool("convert_ad_to_bs", {})

    result = anyio.run(scenario)
    assert result.isError is True
    assert "Input validation error" in result.content[0].text
    assert parva_http_stub["calls"] == []


def test_manifest_cli_works() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "parva_mcp_server.server", "--manifest"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=15,
    )
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert json.loads(proc.stdout)["execution"]["mode"] == "http_agent_gateway"


def test_check_and_compatibility_clis_work() -> None:
    commands = (
        [sys.executable, "-m", "parva_mcp_server.server", "--check"],
        [sys.executable, "integrations/mcp/server.py", "--check"],
    )
    for command in commands:
        proc = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )
        assert proc.returncode == 0, proc.stderr
        assert proc.stderr == ""
        assert json.loads(proc.stdout)["ok"] is True


def test_live_check_executes_http_bridge(parva_http_stub: dict[str, Any]) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "parva_mcp_server.server", "--check-live"],
        cwd=PROJECT_ROOT,
        env=_server_environment(parva_http_stub["origin"]),
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ""
    payload = json.loads(proc.stdout)
    assert payload["live_probe"]["ok"] is True
    assert payload["live_probe"]["manifest_only"] is False
