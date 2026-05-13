from __future__ import annotations

from app.bootstrap.app_factory import create_app
from app.services.agent_service import (
    agent_tools_payload,
    check_human_review_payload,
    draft_rule_payload,
    plan_schedule_payload,
    resolve_intent_payload,
    run_tool_payload,
    verify_temporal_claim_payload,
)
from fastapi.testclient import TestClient


def test_tool_registry_contains_supported_public_tools() -> None:
    names = {tool["name"] for tool in agent_tools_payload()["tools"]}
    assert "parva.verify_temporal_claim" in names
    assert "parva.plan_schedule" in names
    assert "parva.simulate_impact" in names


def test_intent_resolver_detects_claim() -> None:
    result = resolve_intent_payload("2083-01-01 BS maps to 2026-04-14 AD.")
    assert result["recommended_tool"] in {"parva.convert_date", "parva.verify_temporal_claim"}


def test_claim_checker_verifies_false_and_unsupported_cases() -> None:
    assert verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-14 AD.")["status"] == "verified"
    false_result = verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-15 AD.")
    assert false_result["status"] == "false"
    assert false_result["decision"]["requires_human_review"] is True
    unsupported = verify_temporal_claim_payload("This unsupported legal claim is official.")
    assert unsupported["status"] in {"unsupported", "needs_review"}


def test_schedule_planner_uses_rulelang_and_review_gates() -> None:
    schedule = plan_schedule_payload(schedule_type="payroll", bs_year=2082, months=[1, 2])
    assert len(schedule["items"]) == 2
    assert schedule["items"][0]["date"]["bs"]
    review = check_human_review_payload({"use_case": "payroll", "confidence": "source_backed"})
    assert review["requires_human_review"] is True


def test_rule_draft_is_validated_and_review_required() -> None:
    draft = draft_rule_payload("Move exam dates to the next working day if they fall on a holiday.")
    assert draft["validation"]["valid"] is True
    assert draft["decision"]["requires_human_review"] is True


def test_run_tool_is_allowlisted() -> None:
    result = run_tool_payload("parva.verify_temporal_claim", {"claim": "2083-01-01 BS maps to 2026-04-14 AD."})
    assert result["decision"]["status"] == "approved"


def test_agent_api_endpoints() -> None:
    app = create_app()
    client = TestClient(app)
    assert client.get("/v3/api/agent/capabilities").status_code == 200
    response = client.post(
        "/v3/api/agent/verify-claim",
        json={"claim": "2083-01-01 BS maps to 2026-04-14 AD."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "verified"
