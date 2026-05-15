from __future__ import annotations

from parva_mcp_server.manifest import (
    FORBIDDEN_FRAGMENTS,
    build_manifest,
    lint_manifest,
    manifest_digest,
)
from parva_mcp_server.server import UnsafeMcpCall, call_tool, check_server


def test_manifest_lints_clean():
    manifest = build_manifest()
    assert lint_manifest(manifest) == []


def test_manifest_is_read_only_and_optional():
    manifest = build_manifest()
    assert manifest["read_only"] is True
    assert manifest["core_runtime_required"] is False
    assert manifest["security"]["shell_execution"] is False
    assert manifest["security"]["filesystem_writes"] is False


def test_private_admin_billing_routes_are_blocked():
    manifest = build_manifest()
    routes = "\n".join(tool["route"] for tool in manifest["tools"]).lower()
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in routes


def test_resources_tools_and_prompts_exist():
    manifest = build_manifest()
    assert {item["uri"] for item in manifest["resources"]} == {
        "parva://capabilities",
        "parva://route-maturity",
        "parva://source-policy",
        "parva://supported-ranges",
        "parva://known-limitations",
        "parva://benchmark-summary",
    }
    assert {tool["name"] for tool in manifest["tools"]} >= {
        "convert_bs_to_ad",
        "convert_ad_to_bs",
        "check_temporal_claim",
    }
    assert {prompt["name"] for prompt in manifest["prompts"]} == {
        "explain_nepali_date_safely",
        "check_claim_with_sources",
        "plan_schedule_with_review_gates",
    }


def test_manifest_digest_is_stable():
    manifest = build_manifest()
    assert manifest["manifest_sha256"] == manifest_digest(manifest, include_digest=False)


def test_server_check_passes_and_probe_has_claim_boundary():
    result = check_server()
    assert result["ok"] is True
    assert result["probe"]["claim_boundary"] == "decision_support_not_authority"
    assert result["probe"]["review_required"] is True


def test_unsafe_tool_call_is_rejected():
    try:
        call_tool("future_bs_exact_prediction", {})
    except UnsafeMcpCall as exc:
        assert "Unknown" in str(exc)
    else:
        raise AssertionError("unsafe tool call was not rejected")


def test_safe_tool_call_can_use_client_abstraction():
    class FakeClient:
        def request(self, method, route, payload):
            return {"method": method, "route": route, "payload": payload}

    result = call_tool("get_fiscal_year", {"bs_year": 2082}, client=FakeClient())
    assert result["route"] == "/v3/api/enterprise/fiscal-year/2082"
    assert result["claim_boundary"] == "decision_support_not_authority"
