from __future__ import annotations

from parva_mcp_server.manifest import (
    FORBIDDEN_FRAGMENTS,
    build_manifest,
    lint_manifest,
    manifest_digest,
)


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
