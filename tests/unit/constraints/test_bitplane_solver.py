from __future__ import annotations

from app.calendar.bikram_sambat import bs_to_gregorian
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


def test_solver_uses_actual_weekday_bitplane_not_fixed_offsets() -> None:
    result = solve_working_days(bs_year=2082, bs_month=3, count=10)
    weekend_rejections = [item["day"] for item in result["rejected_dates"] if "weekend" in item["reasons"]]

    assert weekend_rejections
    assert weekend_rejections != [4, 11, 18, 25]
    for day in weekend_rejections:
        assert bs_to_gregorian(2082, 3, day).weekday() == 5
    assert result["input_bitplane_hashes"]["working_day"].startswith("sha256:")
    assert result["candidate_mask_hash"].startswith("sha256:")


def test_solver_rejected_dates_include_causal_stamps() -> None:
    result = solve_working_days(bs_year=2082, bs_month=3, count=5, holidays={1})

    assert result["rejected_dates"][0]["causal_stamps"]
    assert result["proof_pack"]["planes"]["working_day"]["cause_stamps"]
