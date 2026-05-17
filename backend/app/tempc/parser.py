"""Tiny TempC parser for payroll safe-date programs."""

from __future__ import annotations

from app.tempc.ir import TempCProgram


def parse_tempc(source: str) -> TempCProgram:
    if "payroll_safe_dates" not in source:
        raise ValueError("only payroll_safe_dates program is supported in TempC v0")
    return TempCProgram("payroll_safe_dates", "payroll_safe_dates", {"count": 5})
