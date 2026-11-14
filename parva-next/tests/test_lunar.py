"""Astronomy against external truth, never against itself."""

from datetime import UTC, date, datetime, timedelta

import pytest

pytest.importorskip("swisseph")
from parva import astro, festivals, lunar

UTC = UTC


def test_sunrise_kathmandu_matches_published_value() -> None:
    # 14 April 2025, Kathmandu: sunrise 05:40 NPT (timeanddate.com / Hamro Patro)
    rise = astro.sunrise(date(2025, 4, 14)).astimezone(astro.NPT)
    assert abs((rise - datetime(2025, 4, 14, 5, 40, tzinfo=astro.NPT)).total_seconds()) < 90


def test_new_moon_matches_usno() -> None:
    # USNO / NASA: new moon 2026-06-15 02:54 UTC
    nm = astro.new_moons(datetime(2026, 6, 1, tzinfo=UTC), 1)[0]
    assert abs((nm - datetime(2026, 6, 15, 2, 54, tzinfo=UTC)).total_seconds()) < 15 * 60


def test_mesha_sankranti_falls_within_a_day_of_1_baishakh() -> None:
    # The table, not the ingress instant, decides the civil day (see parva/lunar.py); but they must be adjacent.
    for ad_year, first_baishakh in ((2024, date(2024, 4, 13)), (2025, date(2025, 4, 14)), (2026, date(2026, 4, 14))):
        t, _ = next(s for s in astro.sankrantis(datetime(ad_year, 4, 1, tzinfo=UTC), 2) if s[1] == 0)
        assert abs((t.astimezone(astro.NPT).date() - first_baishakh).days) <= 1, (ad_year, t)


def test_adhik_months() -> None:
    # 2023: Adhik Shrawan (18 Jul - 16 Aug); 2026: Adhik Jestha (17 May - 15 Jun); 2024, 2025: none.
    adhik = {
        y: [(m.name, m.start.astimezone(astro.NPT).date()) for m in lunar.months(y) if m.adhik and m.start.year == y]
        for y in (2023, 2024, 2025, 2026)
    }
    assert adhik[2023] == [("Adhik Shrawan", date(2023, 7, 18))]
    assert adhik[2026] == [("Adhik Jestha", date(2026, 5, 17))]
    assert adhik[2024] == adhik[2025] == []


def test_months_are_named_by_the_sankranti_inside_them() -> None:
    for m in lunar.months(2025):
        inside = [r for t, r in astro.sankrantis(m.start - timedelta(days=1), 3) if m.start <= t < m.end]
        if m.adhik:
            assert not inside
        else:
            assert inside and lunar.RASHI_TO_MONTH[inside[0]] == m.index


@pytest.mark.parametrize(
    ("fid", "year", "expected"),
    [
        ("vijaya-dashami", 2024, "2024-10-12"),  # tika was Saturday 12 Oct; udaya Dashami was the 13th: aparahna rule
        ("vijaya-dashami", 2025, "2025-10-02"),
        ("vijaya-dashami", 2023, "2023-10-24"),
        ("laxmi-puja", 2022, "2022-10-24"),  # amavasya began 7 minutes after sunset: pradosh, not the sunset instant
        ("laxmi-puja", 2025, "2025-10-20"),
        ("bhai-tika", 2025, "2025-10-23"),
        ("holi", 2024, "2024-03-24"),
        ("holi", 2025, "2025-03-13"),
        ("shivaratri", 2026, "2026-02-15"),  # gazette 2082: फागुन ३
        ("dashain", 2026, "2026-10-11"),  # the legacy engine said 12 September
    ],
)
def test_engine_against_published_dates(fid: str, year: int, expected: str) -> None:
    assert festivals.engine_date(fid, year) == date.fromisoformat(expected)


def test_engine_agrees_with_every_gazette_within_one_day() -> None:
    compared = agreed = 0
    for year in range(2021, 2028):
        for o in festivals.in_year(year):
            if o.gazette and o.engine:
                compared += 1
                agreed += o.gazette == o.engine
                assert abs((o.engine - o.gazette).days) <= 1, (o.id, year, o.gazette, o.engine)
    assert compared >= 100
    assert agreed / compared >= 0.95, f"{agreed}/{compared}"


def test_panchanga_shape() -> None:
    p = lunar.panchanga(date(2026, 10, 11))  # Ghatasthapana: Ashwin Shukla Pratipada
    assert p["tithi"] == 1 and p["paksha"] == "shukla" and p["lunar_month"] == "Ashwin"
    assert p["sunrise"].startswith("2026-10-11T06:") and p["nakshatra"] in astro.NAKSHATRA


def test_yoga_karana_vara() -> None:
    p = lunar.panchanga(date(2026, 10, 11))  # a Sunday
    assert p["vara"] == "Sunday" and p["vara_ne"] == "आइतबार"
    sun, moon = astro.longitudes(astro.sunrise(date(2026, 10, 11)))
    elong = (moon - sun) % 360
    assert p["karana"] == ("Kimstughna" if elong < 6 else "Bava")
    assert p["yoga"] in lunar.YOGA
    for i in range(30):  # the yoga formula, recomputed independently
        d = date(2026, 10, 1) + timedelta(days=i)
        sun, moon = astro.longitudes(astro.sunrise(d))
        assert lunar.YOGA.index(lunar.panchanga(d)["yoga"]) == int((sun + moon) % 360 // (360 / 27)), d
