"""RuleLang contract checks."""

from __future__ import annotations

import json
from pathlib import Path

from app.bootstrap.app_factory import create_app
from app.main import app
from app.services.rulelang_service import (
    ALLOWED_FUNCTIONS,
    evaluate_custom_rule_payload,
    evaluate_rule_payload,
    load_rules,
    validate_rule_payload,
)
from fastapi.testclient import TestClient

client = TestClient(app)


def test_rulelang_capabilities_are_public_safe() -> None:
    response = client.get("/v3/api/rules/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "parva_rulelang"
    assert body["status"] == "public_preview"
    assert body["publication_status"] == "computed_prediction_not_official"
    assert "eval" not in body["builtins"]
    assert "shell_commands" in body["not_allowed"]
    assert body["safety_limits"]["absolute_loop_max_iterations"] == 366


def test_public_rule_registry_loads_and_private_rules_do_not_leak() -> None:
    response = client.get("/v3/api/rules")

    assert response.status_code == 200
    body = response.json()
    rule_ids = {rule["rule_id"] for rule in body["rules"]}
    local_drive_marker = "D:" + "\\"
    assert len(rule_ids) >= 5
    assert "last_working_day_of_nepali_month" in rule_ids
    assert all(rule["status"] != "private" for rule in body["rules"])
    assert all(local_drive_marker not in json.dumps(rule) for rule in body["rules"])


def test_rule_detail_validation_and_embedded_test_endpoint_work() -> None:
    detail = client.get("/v3/api/rules/last_working_day_of_nepali_month")
    test_response = client.post("/v3/api/rules/last_working_day_of_nepali_month/test")

    assert detail.status_code == 200
    assert detail.json()["validation"]["valid"] is True
    assert detail.json()["rule"]["steps"]
    assert test_response.status_code == 200
    assert test_response.json()["summary"]["failed"] == 0


def test_rule_evaluation_returns_decision_trace_meta_and_fact_ids() -> None:
    response = client.post(
        "/v3/api/rules/last_working_day_of_nepali_month/evaluate",
        json={
            "input": {
                "bs_month": "2082-04",
                "profile_id": "nepal_private_company_default",
            }
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["rule_id"] == "last_working_day_of_nepali_month"
    assert body["decision"]["status"] == "approved"
    assert body["decision"]["requires_human_review"] is False
    assert body["output"]["payroll_date"]["bs"] == "2082-04-30"
    assert body["trace"]["steps"]
    assert "fact_month_length_bs_2082_04" in body["fact_ids"]
    assert body["meta"]["claim_boundary"] == "enterprise_decision_support_not_legal_authority"


def test_while_loop_rule_moves_weekend_backward() -> None:
    response = client.post(
        "/v3/api/rules/payroll_previous_working_day_if_non_working/evaluate",
        json={
            "input": {
                "bs_date": "2082-04-03",
                "profile_id": "nepal_private_company_default",
            }
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["output"]["payroll_date"]["bs"] == "2082-04-02"
    assert body["decision"]["status"] == "approved"
    assert any(step["operation"] == "while" for step in body["trace"]["steps"])


def test_next_working_day_fiscal_and_add_working_days_rules_work() -> None:
    next_day = evaluate_rule_payload(
        "next_working_day_if_holiday",
        {"bs_date": "2082-01-01", "profile_id": "nepal_private_company_default"},
    )
    fiscal = evaluate_rule_payload(
        "fiscal_period_for_date",
        {"bs_date": "2082-04-02", "profile_id": "nepal_private_company_default"},
    )
    added = evaluate_rule_payload(
        "add_n_working_days",
        {
            "bs_date": "2082-04-02",
            "working_days": 2,
            "profile_id": "nepal_private_company_default",
        },
    )

    assert next_day["decision"]["status"] == "approved"
    assert next_day["output"]["working_date"]["bs"] == "2082-01-02"
    assert fiscal["output"]["fiscal_period"]["fiscal_month"] == 1
    assert fiscal["decision"]["status"] == "approved"
    assert added["output"]["target_date"]["bs"] == "2082-04-05"
    assert added["decision"]["status"] == "approved"


def test_unknown_and_forbidden_functions_are_rejected() -> None:
    base_rule = {
        "rule_id": "fixture_invalid_function_rule",
        "version": "1.0.0",
        "label": "Invalid function",
        "description": "Invalid public-safe test rule.",
        "status": "fixture_only",
        "inputs": {"bs_date": {"type": "bs_date", "required": True}},
        "outputs": {"result": {"type": "object"}},
        "steps": [
            {
                "set": {
                    "name": "result",
                    "value": {"call": "eval", "args": {"code": "1 + 1"}},
                }
            },
            {"return": {"result": "$var.result"}},
        ],
        "risk_policy": {
            "require_confidence_at_least": "source_backed",
            "block_research_preview": True,
            "block_disputed_facts": True,
            "unsupported_result_action": "human_review_required",
        },
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
    }

    validation = validate_rule_payload(base_rule)
    assert validation["valid"] is False
    assert any("forbidden function eval" in error for error in validation["errors"])

    base_rule["steps"][0]["set"]["value"]["call"] = "unsupported_calendar_magic"
    validation = validate_rule_payload(base_rule)
    assert validation["valid"] is False
    assert any(
        "unsupported function unsupported_calendar_magic" in error for error in validation["errors"]
    )


def test_loop_limits_fail_with_structured_reason_code() -> None:
    rule = _fixture_loop_rule()
    result = evaluate_custom_rule_payload(rule, {"bs_date": "2082-04-04"})

    assert result["decision"]["status"] == "failed"
    assert "MAX_ITERATIONS_EXCEEDED" in result["decision"]["reason_codes"]
    assert result["trace"]["steps"]


def test_risk_policy_low_confidence_requires_review() -> None:
    rule = _fixture_last_day_rule("official_only_fixture", minimum="official_verified")
    result = evaluate_custom_rule_payload(rule, {"bs_month": "2070-01"})

    assert result["decision"]["status"] == "review_required"
    assert result["decision"]["requires_human_review"] is True
    assert "SOURCE_CONFIDENCE_TOO_LOW" in result["decision"]["reason_codes"]


def test_disputed_timegraph_fact_is_blocked_by_policy() -> None:
    rule = {
        "rule_id": "fixture_disputed_fact_rule",
        "version": "1.0.0",
        "label": "Disputed fact fixture",
        "description": "Fixture that references the public TimeGraph conflict.",
        "status": "fixture_only",
        "inputs": {"marker": {"type": "string", "required": False, "default": "fixture"}},
        "outputs": {"disputed": {"type": "boolean"}},
        "steps": [
            {
                "set": {
                    "name": "disputed",
                    "value": {
                        "call": "fact_is_disputed",
                        "args": {"fact_id": "fact_fixture_conflict_candidate_a"},
                    },
                }
            },
            {"return": {"disputed": "$var.disputed"}},
        ],
        "risk_policy": {
            "require_confidence_at_least": "fixture",
            "block_research_preview": True,
            "block_disputed_facts": True,
            "unsupported_result_action": "human_review_required",
        },
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
    }

    result = evaluate_custom_rule_payload(rule, {})

    assert result["decision"]["status"] == "blocked"
    assert "DISPUTED_FACT_BLOCKED" in result["decision"]["reason_codes"]
    assert "fact_fixture_conflict_candidate_a" in result["fact_ids"]


def test_custom_rule_api_and_explain_endpoint_work() -> None:
    rule = _fixture_last_day_rule("custom_public_last_day_fixture")
    evaluate_response = client.post(
        "/v3/api/rules/evaluate",
        json={"rule": rule, "input": {"bs_month": "2082-04"}},
    )
    explain_response = client.post(
        "/v3/api/rules/explain",
        json={
            "rule_id": "last_working_day_of_nepali_month",
            "input": {
                "bs_month": "2082-04",
                "profile_id": "nepal_private_company_default",
            },
        },
    )

    assert evaluate_response.status_code == 200
    assert evaluate_response.json()["decision"]["status"] == "approved"
    assert explain_response.status_code == 200
    assert explain_response.json()["trace"]["steps"]
    assert (
        "Rule last_working_day_of_nepali_month" in explain_response.json()["explanation"]["summary"]
    )


def test_rule_execution_evidence_packet_integrates_with_trust_layer() -> None:
    response = client.post(
        "/v3/api/trust/evidence/rule-execution",
        json={
            "rule_id": "last_working_day_of_nepali_month",
            "input": {
                "bs_month": "2082-04",
                "profile_id": "nepal_private_company_default",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["packet_type"] == "rule_execution"
    assert body["input"]["rule_id"] == "last_working_day_of_nepali_month"
    assert body["fact_ids"]
    assert body["integrity"]["packet_hash"].startswith("sha256:")


def test_public_demo_profile_includes_rules_but_not_full_compliance_routes(monkeypatch) -> None:
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    public_demo_client = TestClient(create_app())

    assert public_demo_client.get("/v3/api/rules/capabilities").status_code == 200
    assert public_demo_client.get("/v3/api/compliance/profiles").status_code == 404
    paths = public_demo_client.get("/openapi.json").json()["paths"]
    assert "/v3/api/rules/capabilities" in paths
    assert "/v3/api/rules/last_working_day_of_nepali_month/evaluate" not in paths
    assert "/v3/api/compliance/profiles" not in paths


def test_static_openapi_docs_exclude_rulelang_preview_surface() -> None:
    schema = json.loads(Path("docs/api-docs/openapi.json").read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]

    assert "RuleDefinition" not in schemas
    assert "RuleExecutionResult" not in schemas
    assert "RuleTraceStep" not in schemas
    assert "/v3/api/rules/capabilities" not in schema["paths"]


def test_rulelang_does_not_expose_unsafe_execution_surface() -> None:
    assert "eval" not in ALLOWED_FUNCTIONS
    assert "exec" not in ALLOWED_FUNCTIONS
    serialized = json.dumps(load_rules(include_private=False))

    assert "source_archive" not in serialized
    assert "private" not in {rule["status"] for rule in load_rules(include_private=False)}


def _fixture_last_day_rule(rule_id: str, *, minimum: str = "source_backed") -> dict[str, object]:
    return {
        "rule_id": rule_id,
        "version": "1.0.0",
        "label": "Fixture last day",
        "description": "Fixture custom rule for tests.",
        "status": "fixture_only",
        "inputs": {"bs_month": {"type": "bs_month", "required": True}},
        "outputs": {"last_day": {"type": "date"}},
        "steps": [
            {
                "set": {
                    "name": "last_day",
                    "value": {
                        "call": "last_day_of_nepali_month",
                        "args": {"bs_month": "$input.bs_month"},
                    },
                }
            },
            {"return": {"last_day": "$var.last_day"}},
        ],
        "risk_policy": {
            "require_confidence_at_least": minimum,
            "block_research_preview": True,
            "block_disputed_facts": True,
            "unsupported_result_action": "human_review_required",
        },
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
    }


def _fixture_loop_rule() -> dict[str, object]:
    return {
        "rule_id": "fixture_loop_limit_rule",
        "version": "1.0.0",
        "label": "Loop limit fixture",
        "description": "Fixture custom rule for max iteration failure.",
        "status": "fixture_only",
        "inputs": {"bs_date": {"type": "bs_date", "required": True}},
        "outputs": {"result": {"type": "object"}},
        "steps": [
            {"set": {"name": "candidate", "value": "$input.bs_date"}},
            {
                "while": {
                    "condition": True,
                    "max_iterations": 1,
                    "do": [
                        {
                            "set": {
                                "name": "candidate",
                                "value": {
                                    "call": "subtract_days",
                                    "args": {"date": "$var.candidate", "days": 1},
                                },
                            }
                        }
                    ],
                }
            },
            {"return": {"result": "$var.candidate"}},
        ],
        "risk_policy": {
            "require_confidence_at_least": "source_backed",
            "block_research_preview": True,
            "block_disputed_facts": True,
            "unsupported_result_action": "human_review_required",
        },
        "claim_boundary": "enterprise_decision_support_not_legal_authority",
    }
