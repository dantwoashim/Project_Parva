from __future__ import annotations

from app.calendar.bs_year import bs_solar_year_for_gregorian_year


def test_bs_solar_year_mapping_uses_month_aware_rule():
    assert bs_solar_year_for_gregorian_year(2026, 1) == 2083
    assert bs_solar_year_for_gregorian_year(2026, 9) == 2083
    assert bs_solar_year_for_gregorian_year(2026, 10) == 2082
    assert bs_solar_year_for_gregorian_year(2026, 12) == 2082
