from __future__ import annotations

from app.services import rulelang_service

from .test_no_eval_exec import _base_rule


def test_rulelang_function_call_budget_is_enforced(monkeypatch):
    monkeypatch.setattr(rulelang_service, "MAX_FUNCTION_CALLS", 1)
    rule = _base_rule(
        {
            "call": {
                "function": "validate_date",
                "args": {"date": "$input.date"},
            }
        }
    )
    rule["steps"].insert(
        1,
        {
            "call": {
                "function": "validate_date",
                "args": {"date": "$input.date"},
            }
        },
    )

    result = rulelang_service.execute_rule(rule, {"date": "2080-01-01"})

    assert result["decision"]["status"] == "failed"
    assert "MAX_FUNCTION_CALLS_EXCEEDED" in result["decision"]["reason_codes"]
