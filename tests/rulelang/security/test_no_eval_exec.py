from __future__ import annotations

from app.services import rulelang_service


def _base_rule(step: dict) -> dict:
    return {
        "rule_id": "security_probe",
        "version": "1.0.0",
        "label": "Security probe",
        "description": "Fixture-only RuleLang security probe.",
        "status": "fixture_only",
        "inputs": {"date": {"type": "bs_date", "required": True}},
        "outputs": {"ok": {"type": "boolean"}},
        "steps": [step, {"return": {"ok": True}}],
        "risk_policy": {
            "require_confidence_at_least": "calculated",
            "unsupported_result_action": "human_review_required",
            "future_date_action": "human_review_required",
        },
        "claim_boundary": rulelang_service.RULELANG_CLAIM_BOUNDARY,
    }


def test_rulelang_rejects_forbidden_direct_function_calls():
    validation = rulelang_service.validate_rule_payload(
        _base_rule({"call": {"function": "eval", "args": {"date": "$input.date"}}})
    )

    assert validation["valid"] is False
    assert any("forbidden function eval" in error for error in validation["errors"])


def test_rulelang_rejects_forbidden_nested_function_calls():
    validation = rulelang_service.validate_rule_payload(
        _base_rule({"return": {"ok": {"call": "exec", "args": {"date": "$input.date"}}}})
    )

    assert validation["valid"] is False
    assert any("forbidden function exec" in error for error in validation["errors"])
