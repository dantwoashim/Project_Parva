from __future__ import annotations

from app.services import rulelang_service


def _call_limit_rule(call_count: int) -> dict:
    return {
        "rule_id": "call_limit_probe",
        "version": "1.0.0",
        "label": "Call limit probe",
        "description": "Fixture rule used to verify the independent function-call counter.",
        "status": "fixture_only",
        "inputs": {"date": {"type": "bs_date", "required": True}},
        "outputs": {"ok": {"type": "boolean"}},
        "steps": [
            {
                "call": {
                    "function": "validate_date",
                    "args": {"date": "$input.date"},
                }
            }
            for _ in range(call_count)
        ]
        + [{"return": {"ok": True}}],
        "risk_policy": {
            "require_confidence_at_least": "calculated",
            "unsupported_result_action": "human_review_required",
            "future_date_action": "human_review_required",
        },
        "claim_boundary": rulelang_service.RULELANG_CLAIM_BOUNDARY,
    }


def test_rulelang_function_calls_are_independently_bounded(monkeypatch):
    monkeypatch.setattr(rulelang_service, "MAX_FUNCTION_CALLS", 3)

    result = rulelang_service.execute_rule(
        _call_limit_rule(5),
        {"date": "2080-01-01"},
    )

    assert result["decision"]["status"] == "failed"
    assert "MAX_FUNCTION_CALLS_EXCEEDED" in result["decision"]["reason_codes"]
    assert result["trace"]["function_calls"] == 4
    assert result["trace"]["max_function_calls"] == 3
