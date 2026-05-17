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


def test_expanded_bitplanes_include_fiscal_festival_and_overlay_causes() -> None:
    from app.forge.bitplanes import build_month_bitplanes

    planes = build_month_bitplanes(
        bs_year=2082,
        bs_month=4,
        festival_windows={"dashain": {10, 11}},
        overlay_days={15},
    )

    assert "fiscal_period" in planes
    assert "festival_window:dashain" in planes
    assert "overlay:branch" in planes
    assert all(planes["fiscal_period"].bits)
    assert planes["festival_window:dashain"].bits[9] is True
    assert planes["overlay:branch"].cause_stamps[14]["reason"] == "overlay_branch_applied"
