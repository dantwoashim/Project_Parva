"""Interpret TempC programs."""

from __future__ import annotations

from app.tempc.ir import TempCProgram
from app.workflows.payroll import payroll_safe_dates


def run_tempc(program: TempCProgram, *, bs_year: int, bs_month: int) -> dict:
    if program.operation not in {"payroll_safe_dates", "payroll_schedule"}:
        raise ValueError("unsupported TempC operation")
    effective_year = int(program.parameters.get("bs_year", bs_year))
    effective_month = int(program.parameters.get("bs_month", bs_month))
    result = payroll_safe_dates(effective_year, effective_month, int(program.parameters.get("count", 5)))
    result["tempc"] = {
        "program": program.name,
        "operation": program.operation,
        "statements": list(program.statements),
        "compiled_constraint_query": {
            "bs_year": effective_year,
            "bs_month": effective_month,
            "count": int(program.parameters.get("count", 5)),
            "policy": program.parameters.get("policy", "canonical@0.1.0"),
            "operation": "working_days",
        },
        "boundary": "workflow_decision_support_not_payroll_authority",
    }
    return result
