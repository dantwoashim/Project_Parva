"""Payroll-safe date workflow."""

from __future__ import annotations

from app.constraints.solver import solve_working_days


def payroll_safe_dates(bs_year: int, bs_month: int, count: int = 5) -> dict:
    return solve_working_days(bs_year=bs_year, bs_month=bs_month, count=count, holidays={1})
