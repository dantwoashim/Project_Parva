"""Solar ingress solver tests."""

from datetime import datetime, timezone

from app.research.future_bs.solar_ingress_solver import bracket_crossing, solve_solar_ingress


def test_solar_ingress_solver_returns_event_payload():
    event = solve_solar_ingress(0, datetime(2027, 4, 1, tzinfo=timezone.utc))

    assert event.sign == "Mesha"
    assert event.bs_month_name == "Baishakh"
    assert event.payload()["calculation_version"] == "solar_ingress_solver_v1"


def test_solar_ingress_solver_brackets_wraparound_crossing():
    low, high = bracket_crossing(0, datetime(2027, 4, 1, tzinfo=timezone.utc))

    assert low < high
