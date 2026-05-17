"""Interpret TempC programs."""

from __future__ import annotations

from app.tempc.ir import TempCProgram
from app.workflows.payroll import payroll_safe_dates


def run_tempc(program: TempCProgram, *, bs_year: int, bs_month: int) -> dict:
    if program.operation != "payroll_safe_dates":
        raise ValueError("unsupported TempC operation")
    return payroll_safe_dates(bs_year, bs_month, int(program.parameters.get("count", 5)))
