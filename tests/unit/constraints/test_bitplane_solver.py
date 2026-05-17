from __future__ import annotations

from app.constraints.solver import solve_working_days


def test_solver_finds_working_days_and_explains_rejections() -> None:
    result = solve_working_days(bs_year=2082, bs_month=3, count=5, holidays={1})
    assert result["kind"] == "constraint_solution"
    assert len(result["selected_days"]) == 5
    assert result["rejected_dates"][0]["reasons"] == ["holiday"]
    assert result["bitplane_witness_refs"]


def test_solver_returns_unsat_membrane_for_impossible_constraints() -> None:
    result = solve_working_days(bs_year=2082, bs_month=3, count=40)
    assert result["membrane_kind"] == "unsat"
    assert "not_enough_working_days" in result["unsat_core"]
