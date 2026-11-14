"""Check packaged evidence against its archived sources and regression fixtures."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from parva import bs, holidays
from parva.evidence import read_data


def verify(archive_root: Path) -> dict:
    sources = read_data("SOURCES.json")
    release = read_data("release.json")
    review_states: Counter = Counter()
    rows_checked = 0
    for year in holidays.covered_years():
        source = sources[f"moha-{year}"]
        pdf = archive_root / f"{year}_public_holidays.pdf"
        assert pdf.is_file(), f"Missing archived source: {pdf}"
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == source["sha256"], f"Changed source: {pdf}"
        assert pdf.stat().st_size == source["size_bytes"], f"Changed source size: {pdf}"
        assert holidays.coverage(year) == "partial", "Completeness requires a separate evidence review."
        seen = set()
        for row in holidays.of_year(year, "all"):
            key = (row["id"], row["ad"])
            assert key not in seen, f"Duplicate row: {year} {key}"
            seen.add(key)
            value = bs.parse(row["bs"])
            assert value.year == year and value.ad.isoformat() == row["ad"], key
            assert type(row["days"]) is int and 1 <= row["days"] <= 15, key
            assert bs.to_bs(value.ad + timedelta(days=row["days"] - 1)).year == year, key
            for scope in row.get("scopes", [row["scope"]]):
                holidays.validate_scope(scope)
            if row["weekday_verified"]:
                named = [i for i, day in enumerate(bs.WEEKDAYS_NE) if day in row["text"]]
                if named:
                    assert value.ad.weekday() in named, f"Weekday mismatch: {year} {key}"
            if row["review"] == "source_checked":
                assert 1 <= row["source_page"] <= 20 and row["text"], key
            review_states[row["review"]] += 1
            rows_checked += 1

    fixture = Path(__file__).resolve().parents[1] / "tests/fixtures/official_holdout_2078_2083.csv"
    with fixture.open(encoding="utf-8") as handle:
        months_checked = 0
        for row in csv.DictReader(handle):
            for month, name in enumerate(bs.NAMES, start=1):
                assert bs.month_days(int(row["bs_year"]), month) == int(row[name.lower()]), (row["bs_year"], name)
                months_checked += 1

    day = bs.START[bs.MIN_YEAR]
    dates_checked = 0
    while day < bs.END:
        assert bs.to_ad(*bs.to_bs(day)) == day, day
        day += timedelta(days=1)
        dates_checked += 1

    # Endpoints independently transcribed from the source images, not inferred durations.
    for year, identifier, start, end in (
        (2083, "dashain-holidays", "2083-06-31", "2083-07-06"),
        (2083, "tihar-holidays", "2083-07-22", "2083-07-26"),
        (2082, "dashain-holidays", "2082-06-13", "2082-06-18"),
        (2082, "tihar-holidays", "2082-07-03", "2082-07-07"),
    ):
        row = next(row for row in holidays.of_year(year) if row["id"] == identifier)
        assert row["bs"] == start
        assert date.fromisoformat(row["ad"]) + timedelta(days=row["days"] - 1) == bs.parse(end).ad

    return {
        "data_version": release["version"],
        "data_sha256": bs.DATA_SHA256,
        "archived_sources_verified": len(holidays.covered_years()),
        "holiday_rows_checked": rows_checked,
        "review_states": dict(review_states),
        "fixture_months_matched": months_checked,
        "conversion_dates_round_tripped": dates_checked,
        "coverage": release["coverage"],
        "limitations": release["limits"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, default=Path("../data/source_archive/moha"))
    args = parser.parse_args()
    print(json.dumps(verify(args.archive_root), indent=2))
