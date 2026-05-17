from __future__ import annotations

from pathlib import Path

from app.tempc.compiler import compile_tempc
from app.tempc.interpreter import run_tempc


def test_tempc_payroll_program_runs_schedule() -> None:
    source = Path("examples/tempc/payroll_safe_dates.tempc").read_text(encoding="utf-8")
    program = compile_tempc(source)
    result = run_tempc(program, bs_year=2082, bs_month=4)
    assert result["kind"] == "constraint_solution"
    assert len(result["selected_days"]) == 5
    assert result["tempc"]["compiled_constraint_query"]["operation"] == "working_days"
    assert result["tempc"]["boundary"] == "workflow_decision_support_not_payroll_authority"


def test_tempc_parses_let_working_days_and_emit() -> None:
    source = """
    program payroll {
      let month = bs_month(2082, 4)
      let days = working_days(in: month, exclude: holidays())
      emit payroll_schedule(days, policy: "canonical@0.1.0")
    }
    """

    program = compile_tempc(source)

    assert program.operation == "payroll_schedule"
    assert program.parameters["bs_year"] == 2082
    assert program.parameters["bs_month"] == 4
    assert program.parameters["policy"] == "canonical@0.1.0"
    assert len(program.statements) == 3


def test_tempc_invalid_program_returns_diagnostic() -> None:
    source = """
    program payroll {
      let days = working_days(in: missing, exclude: holidays())
      emit payroll_schedule(days, policy: "canonical@0.1.0")
    }
    """

    try:
        compile_tempc(source)
    except ValueError as exc:
        assert "binding not found" in str(exc)
    else:
        raise AssertionError("invalid TempC program should fail")
