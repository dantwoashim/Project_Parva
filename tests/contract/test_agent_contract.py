from __future__ import annotations

from datetime import date, datetime, timezone

from app.bootstrap.app_factory import create_app
from app.core.clock import FixedClock
from app.services.agent_service import (
    AgentError,
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
    assert "parva.get_festival_date" in names
    assert "parva.get_panchanga_summary" in names
    assert "parva.get_benchmark_summary" in names


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
    assert unsupported["decision"]["requires_human_review"] is True
    assert unsupported["decision"]["status"] == "review_required"


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
    assert result["evidence"]["fact_ids"]


def test_run_tool_normalizes_invalid_bs_dates() -> None:
    try:
        run_tool_payload("parva.convert_date", {"bs_date": "2082-04-32"})
    except AgentError as exc:
        assert exc.code == "INVALID_INPUT"
        assert exc.status_code == 400
    else:
        raise AssertionError("invalid BS date was accepted")


def test_run_tool_reads_current_benchmark_artifact() -> None:
    result = run_tool_payload("parva.get_benchmark_summary", {})
    summary = result["result"]
    assert summary["task_count"] == 64
    assert summary["parva_score_percent"] == 86.09


def test_today_tool_uses_the_supplied_nepal_civil_date() -> None:
    result = run_tool_payload("parva.get_today", {}, today=date(2026, 7, 16))

    assert result["result"]["gregorian"] == "2026-07-16"


def test_agent_api_today_tracks_kathmandu_midnight() -> None:
    app = create_app()
    app.state.clock = FixedClock(datetime(2026, 7, 15, 18, 15, tzinfo=timezone.utc))
    client = TestClient(app)

    response = client.post(
        "/v3/api/agent/run-tool",
        json={"tool_name": "parva.get_today", "input": {}},
    )

    assert response.status_code == 200
    assert response.json()["result"]["gregorian"] == "2026-07-16"


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
    invalid = client.post(
        "/v3/api/agent/run-tool",
        json={"tool_name": "parva.convert_date", "input": {"bs_date": "2082-04-32"}},
    )
    assert invalid.status_code == 400
    assert invalid.json()["detail"]["code"] == "INVALID_INPUT"
