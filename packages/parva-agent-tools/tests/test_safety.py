from __future__ import annotations

from parva_tools.descriptor_lint import lint_tool_descriptors
from parva_tools.langchain import build_langchain_tools, call_tool
from parva_tools.llamaindex import build_llamaindex_tools
from parva_tools.safety import (
    FORBIDDEN_ROUTE_FRAGMENTS,
    normalize_tool_response,
    validate_tool_specs,
)
from parva_tools.schemas import TOOL_SPECS


class FakeClient:
    def request(self, method, route, payload):
        return {
            "method": method,
            "route": route,
            "payload": payload,
            "source_tier": "public",
            "confidence": "high",
            "supported_range": "public_supported_range",
            "claim_boundary": "decision_support_not_authority",
            "review_required": payload.get("review_required", False),
        }


def test_tool_specs_are_public_safe():
    validate_tool_specs()
    routes = "\n".join(spec.route for spec in TOOL_SPECS).lower()
    for fragment in FORBIDDEN_ROUTE_FRAGMENTS:
        assert fragment not in routes


def test_every_tool_schema_includes_claim_boundary_contract():
    for spec in TOOL_SPECS:
        assert "claim_boundary" in spec.output_contract
        assert spec.route.startswith("/v3/api/")


def test_descriptions_do_not_claim_authority():
    unsafe = ["official future", "government approved", "legal authority", "banking authority"]
    for spec in TOOL_SPECS:
        lowered = spec.description.lower()
        assert not any(phrase in lowered for phrase in unsafe)
    assert lint_tool_descriptors() == []


def test_review_required_behavior_is_preserved():
    payload = normalize_tool_response({"publication_status": "computed_prediction_not_official"})
    assert payload["review_required"] is True
    assert "not official" not in str(payload["not_authority"]).lower()


def test_every_tool_output_contract_preserves_review_required():
    for spec in TOOL_SPECS:
        assert "review_required" in spec.output_contract
        assert "claim_boundary" in spec.output_contract


def test_langchain_and_llamaindex_fallback_descriptors_are_safe():
    assert len(build_langchain_tools()) == len(TOOL_SPECS)
    assert len(build_llamaindex_tools()) == len(TOOL_SPECS)


def test_call_tool_uses_public_route_client_shape():
    result = call_tool("parva_get_fiscal_year", {"bs_year": 2082}, client=FakeClient())
    assert result["answer"]["route"] == "/v3/api/enterprise/fiscal-year/{bs_year}"
    assert result["claim_boundary"] == "decision_support_not_authority"


def test_tool_names_are_exact_public_safe_set():
    assert {spec.name for spec in TOOL_SPECS} == {
        "parva_convert_bs_to_ad",
        "parva_convert_ad_to_bs",
        "parva_get_today_nepali_date",
        "parva_check_holiday",
        "parva_get_working_day_status",
        "parva_get_fiscal_year",
        "parva_get_festival_date",
        "parva_get_panchanga_summary",
        "parva_check_temporal_claim",
    }
