from __future__ import annotations

from pathlib import Path
from typing import Any

from parva_mcp_server.manifest import (
    AGENT_GATEWAY_ROUTE,
    FORBIDDEN_FRAGMENTS,
    build_manifest,
    lint_manifest,
    manifest_digest,
)
from parva_mcp_server.server import (
    InvalidMcpArguments,
    UnsafeMcpCall,
    call_tool,
    check_server,
)


class FakeClient:
    origin = "https://parva.test"

    def __init__(
        self,
        response: dict[str, Any] | None = None,
        *,
        public_tools: list[str] | None = None,
    ) -> None:
        self.calls: list[dict[str, Any]] = []
        self.response = response or {
            "tool_name": "parva.convert_date",
            "result": {"bikram_sambat": {"year": 2083, "month": 1, "day": 1}},
            "decision": {"status": "approved", "requires_human_review": False},
            "meta": {"claim_boundary": "agent_temporal_reasoning_not_legal_authority"},
        }
        self.public_tools = (
            list(public_tools)
            if public_tools is not None
            else sorted(
                {
                    str(tool["agent_tool"])
                    for tool in build_manifest()["tools"]
                }
                | {"parva.get_capabilities", "parva.get_benchmark_summary"}
            )
        )

    def request(self, method: str, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append({"method": method, "route": route, "payload": payload})
        if payload.get("tool_name") == "parva.get_capabilities":
            return {
                "tool_name": "parva.get_capabilities",
                "result": {"public_tools": list(self.public_tools)},
                "decision": {"status": "approved", "requires_human_review": False},
                "meta": {"claim_boundary": "agent_temporal_reasoning_not_legal_authority"},
            }
        return dict(self.response)


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_manifest_lints_clean() -> None:
    manifest = build_manifest()
    assert lint_manifest(manifest) == []
    assert manifest["manifest_sha256"] == manifest_digest(manifest, include_digest=False)


def test_manifest_is_read_only_and_uses_one_gateway() -> None:
    manifest = build_manifest()
    assert manifest["read_only"] is True
    assert manifest["core_runtime_required"] is False
    assert manifest["execution"] == {
        "mode": "http_agent_gateway",
        "route": AGENT_GATEWAY_ROUTE,
        "method": "POST",
    }
    assert {tool["route"] for tool in manifest["tools"]} == {AGENT_GATEWAY_ROUTE}
    assert {tool["method"] for tool in manifest["tools"]} == {"POST"}


def test_private_admin_and_billing_routes_are_blocked() -> None:
    serialized = str(build_manifest()["tools"]).lower()
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in serialized


def test_every_tool_has_a_strict_descriptive_schema() -> None:
    for tool in build_manifest()["tools"]:
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert isinstance(schema["properties"], dict)
        for property_schema in schema["properties"].values():
            assert property_schema.get("type")
            assert property_schema.get("description") or schema["properties"] == {}


def test_tool_call_reaches_agent_gateway_with_adapted_input() -> None:
    client = FakeClient()
    result = call_tool(
        "convert_ad_to_bs",
        {"date": "2026-04-14"},
        client=client,
    )
    assert client.calls == [
        {
            "method": "POST",
            "route": AGENT_GATEWAY_ROUTE,
            "payload": {
                "tool_name": "parva.convert_date",
                "input": {"ad_date": "2026-04-14"},
            },
        }
    ]
    assert result["result"]["bikram_sambat"] == {"year": 2083, "month": 1, "day": 1}
    assert result["review_required"] is False
    assert result["not_authority"] is True


def test_bs_arguments_are_formatted_for_the_agent_gateway() -> None:
    client = FakeClient()
    call_tool(
        "convert_bs_to_ad",
        {"year": 2083, "month": 1, "day": 1},
        client=client,
    )
    assert client.calls[0]["payload"]["input"] == {"bs_date": "2083-01-01"}


def test_valid_bs_day_32_reaches_compliance_gateway() -> None:
    client = FakeClient()
    call_tool("check_working_day", {"bs_date": "2082-03-32"}, client=client)
    assert client.calls[0]["payload"]["input"]["bs_date"] == "2082-03-32"


def test_explicit_nested_review_decision_is_preserved() -> None:
    client = FakeClient(
        {
            "result": {
                "policy": {"publication_status": "computed_prediction_not_official"},
                "decision": {"requires_human_review": True},
            },
            "decision": {"status": "approved", "requires_human_review": False},
        }
    )
    result = call_tool("get_nepali_today", {}, client=client)
    assert result["review_required"] is True


def test_invalid_arguments_are_rejected_before_http() -> None:
    client = FakeClient()
    try:
        call_tool("convert_ad_to_bs", {"date": "14-04-2026"}, client=client)
    except InvalidMcpArguments as exc:
        assert "Invalid arguments" in str(exc)
    else:
        raise AssertionError("invalid date format was accepted")
    assert client.calls == []


def test_unknown_tool_is_rejected_before_http() -> None:
    try:
        call_tool("future_bs_exact_prediction", {}, client=FakeClient())
    except UnsafeMcpCall as exc:
        assert "Unknown" in str(exc)
    else:
        raise AssertionError("unsafe tool call was accepted")


def test_server_check_reports_real_execution_mode() -> None:
    result = check_server(client=FakeClient())
    assert result["ok"] is True
    assert result["protocol_implementation"] == "official-mcp-python-sdk"
    assert result["execution"]["route"] == AGENT_GATEWAY_ROUTE
    assert "probe" not in result


def test_live_server_check_executes_the_bridge() -> None:
    client = FakeClient()
    result = check_server(live=True, client=client)
    assert result["ok"] is True
    assert result["live_probe"]["ok"] is True
    assert result["live_probe"]["manifest_only"] is False
    assert result["live_probe"]["required_agent_tool_count"] == 9
    assert client.calls[0]["payload"]["tool_name"] == "parva.get_capabilities"
    assert client.calls[1]["payload"]["tool_name"] == "parva.convert_date"


def test_live_server_check_rejects_a_stale_gateway() -> None:
    client = FakeClient(public_tools=["parva.convert_date", "parva.get_capabilities"])
    result = check_server(live=True, client=client)

    assert result["ok"] is False
    assert result["live_probe"]["error"]["code"] == "MISSING_AGENT_CAPABILITIES"
    assert "parva.get_festival_date" in result["live_probe"]["missing_agent_tools"]
    assert len(client.calls) == 1


def test_packaged_server_is_the_only_implementation() -> None:
    assert not (PROJECT_ROOT / "parva_mcp_server" / "server.py").exists()
    compatibility_entrypoint = (PROJECT_ROOT / "integrations" / "mcp" / "server.py").read_text(
        encoding="utf-8"
    )
    assert "from parva_mcp_server.server import main" in compatibility_entrypoint
    assert "handle_jsonrpc" not in compatibility_entrypoint
