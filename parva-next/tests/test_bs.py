"""BS <-> AD.  Exhaustive where it can be (the table is only 35,000 days), golden where it must be."""

import hashlib
from datetime import date, timedelta
from pathlib import Path

import pytest

from parva import bs

# (BS, AD) pairs from gazettes and published calendars - not from this code.
GOLDEN = [
    ("2083-01-01", "2026-04-14"),  # MoHA 2083: नव वर्ष - वैशाख १ गते मङ्गलबार (Tuesday)
    ("2082-01-01", "2025-04-14"),  # DoIB table calendar 2082
    ("2081-01-01", "2024-04-13"),  # MoHA 2081: नव वर्ष - वैशाख १ गते शनिबार (Saturday)
    ("2080-01-01", "2023-04-14"),
    ("2083-03-32", "2026-07-16"),  # Ashadh 2083 has 32 days: the payroll boundary bug
    ("2083-04-01", "2026-07-17"),  # 1 Shrawan 2083: fiscal year 2083/84 begins
    ("2083-06-25", "2026-10-11"),  # MoHA 2083: घटस्थापना - असोज २५ गते आइतबार (Sunday)
    ("2083-11-22", "2027-03-06"),  # MoHA 2083: महाशिवरात्री - फागुन २२ गते शनिबार (Saturday)
    ("2000-01-01", "1943-04-14"),  # first day of the table (agrees with nepali-datetime)
]


@pytest.mark.parametrize(("bs_text", "ad_text"), GOLDEN)
def test_golden(bs_text: str, ad_text: str) -> None:
    b, d = bs.parse(bs_text), date.fromisoformat(ad_text)
    assert bs.to_ad(*b) == d
    assert bs.to_bs(d) == b


def test_every_day_round_trips_and_is_monotone() -> None:
    d, previous = bs.START[bs.MIN_YEAR], None
    while d < bs.END:
        b = bs.to_bs(d)
        assert bs.to_ad(*b) == d
        assert previous is None or previous < b, (previous, b)
        previous, d = b, d + timedelta(days=1)


def test_every_year_is_365_or_366_days_of_29_to_32_day_months() -> None:
    for year, months in bs.MONTHS.items():
        assert len(months) == 12 and sum(months) in (365, 366), year
        assert all(29 <= m <= 32 for m in months), year


def test_year_starts_are_consecutive() -> None:
    for year in bs.YEARS[:-1]:
        assert bs.START[year + 1] - bs.START[year] == timedelta(days=sum(bs.MONTHS[year]))


def test_validation() -> None:
    assert bs.is_valid(2083, 3, 32)
    assert not bs.is_valid(2083, 1, 32)
    assert not bs.is_valid(2083, 13, 1)
    assert not bs.is_valid(1999, 1, 1)
    with pytest.raises(ValueError, match="does not exist"):
        bs.to_ad(2082, 1, 32)
    with pytest.raises(ValueError, match="outside the table"):
        bs.to_bs(date(1900, 1, 1))
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        bs.parse("2083/01/01")


def test_devanagari_and_formatting() -> None:
    b = bs.parse("२०८३-०६-२७")
    assert b == bs.BS(2083, 6, 27)
    assert bs.parse("२०८३-०१-०१") == bs.parse("2083-01-01")
    assert b.nepali() == "२०८३ असोज २७, मङ्गलबार"
    assert str(b) == "2083-06-27" and b.month_name == "Ashwin"


def test_data_sha256() -> None:
    root = Path(bs.__file__).parent / "data"
    h = hashlib.sha256()
    for f in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix()):
        h.update(f"{f.relative_to(root).as_posix()}\n".encode())
        h.update(f.read_bytes())
    assert len(bs.DATA_SHA256) == 64 and h.hexdigest() == bs.DATA_SHA256


def test_sources_follow_the_table_ranges() -> None:
    assert "moha-gazette-weekdays" in bs.BS(2083, 1, 1).sources
    assert bs.BS(2090, 1, 1).sources == ("table-provisional",)


def test_agrees_with_nepali_datetime_if_installed() -> None:
    nd = pytest.importorskip("nepali_datetime")
    d = date(1943, 4, 14)
    while d < date(2030, 12, 16):  # before 2087 Mangsir, where nepali-datetime's row was adopted deliberately
        b = bs.to_bs(d)
        assert nd.date(b.year, b.month, b.day).to_datetime_date() == d
        d += timedelta(days=37)  # every ~5 weeks is enough to catch any month drift
