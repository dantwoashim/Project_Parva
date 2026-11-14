"""Holidays and working days come from the gazette, not from a two-entry dictionary."""

from datetime import date

from parva import holidays


def test_the_big_ones_are_not_working_days() -> None:
    assert holidays.is_working_day(date(2026, 10, 11)) is False
    assert holidays.is_working_day(date(2026, 10, 20)) is False
    assert holidays.is_working_day(date(2026, 11, 8)) is False
    assert holidays.is_working_day(date(2026, 4, 14)) is False
    assert holidays.is_working_day(date(2027, 3, 6)) is False
    assert holidays.is_working_day(date(2026, 10, 23)) is False


def test_scopes() -> None:
    teej = date(2026, 9, 14)
    assert holidays.on(teej) == []  # not a holiday for everyone
    assert [h["id"] for h in holidays.on(teej, "women")] == ["teej"]
    assert holidays.is_working_day(teej, scope="women") is False
    assert holidays.is_working_day(teej) is None
    assert [h["id"] for h in holidays.on(date(2026, 9, 25), "kathmandu-valley")] == ["indra-jatra"]


def test_weekends() -> None:
    saturday, friday = date(2026, 9, 12), date(2026, 9, 11)
    assert holidays.is_working_day(saturday) is False
    assert holidays.is_working_day(friday) is None
    assert holidays.is_working_day(friday, weekend=holidays.FRIDAY_SATURDAY) is False
    assert holidays.next_working_day(friday) is None
    assert holidays.previous_working_day(date(2026, 9, 13)) is None


def test_fiscal_year_boundary() -> None:
    assert holidays.fiscal_year(date(2026, 7, 16)) == (2082, date(2025, 7, 17), date(2026, 7, 16))  # Ashadh 32
    assert holidays.fiscal_year(date(2026, 7, 17)) == (2083, date(2026, 7, 17), date(2027, 7, 16))  # Shrawan 1


def test_gazette_rows_are_consistent() -> None:
    for year in holidays.covered_years():
        rows = holidays.of_year(year, "all")
        assert rows and holidays.source(year) == f"moha-{year}"
        for h in rows:
            assert h["bs"].startswith(str(year)) and h["days"] >= 1 and h["text"]
        verified = sum(h["weekday_verified"] for h in rows)
        assert verified / len(rows) > 0.75, (year, verified, len(rows))


def test_gai_jatra_is_the_day_after_janai_purnima_in_every_gazette() -> None:
    for year in holidays.covered_years():
        by_id = {h["id"]: date.fromisoformat(h["ad"]) for h in holidays.of_year(year, "all")}
        if {"gai-jatra", "janai-purnima"} <= by_id.keys():
            assert 0 <= (by_id["gai-jatra"] - by_id["janai-purnima"]).days <= 1, year


def test_working_days_in_dashain_month() -> None:
    # Partial coverage cannot establish a working-day count.
    assert holidays.working_days(date(2026, 10, 1), date(2026, 10, 31)) is None
