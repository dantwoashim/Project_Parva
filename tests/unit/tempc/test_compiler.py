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
