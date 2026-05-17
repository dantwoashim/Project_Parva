from __future__ import annotations

from app.workflows.payroll import payroll_safe_dates


def test_payroll_safe_date_workflow_returns_actionable_dates() -> None:
    result = payroll_safe_dates(2082, 4, count=3)
    assert result["kind"] == "constraint_solution"
    assert result["selected_days"]
    assert result["claim_boundary"] == "solver_decision_support_not_authority"
