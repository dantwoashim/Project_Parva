from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

import pytest
from app.calendar.bikram_sambat import (
    bs_to_gregorian,
    days_in_bs_month,
    gregorian_to_bs,
    is_valid_bs_date,
)


def test_bs_2082_asar_shrawan_month_lengths_match_published_calendar() -> None:
    assert days_in_bs_month(2082, 3) == 32
    assert days_in_bs_month(2082, 4) == 31
    assert is_valid_bs_date(2082, 3, 32) is True
    assert is_valid_bs_date(2082, 4, 32) is False


@pytest.mark.parametrize(
    ("ad_date", "bs_date"),
    [
        (date(2025, 7, 16), (2082, 3, 32)),
        (date(2025, 7, 17), (2082, 4, 1)),
        (date(2025, 8, 16), (2082, 4, 31)),
        (date(2025, 8, 17), (2082, 5, 1)),
    ],
)
def test_bs_2082_asar_shrawan_boundary_is_bijective(
    ad_date: date,
    bs_date: tuple[int, int, int],
) -> None:
    assert gregorian_to_bs(ad_date) == bs_date
    assert bs_to_gregorian(*bs_date) == ad_date


def test_bs_2082_shrawan_32_is_rejected() -> None:
    with pytest.raises(ValueError):
        bs_to_gregorian(2082, 4, 32)


def test_bs_2082_tracked_source_artifacts_match_runtime_table() -> None:
    root = Path(__file__).resolve().parents[2]
    expected = [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
    columns = [
        "baishakh",
        "jestha",
        "ashadh",
        "shrawan",
        "bhadra",
        "ashwin",
        "kartik",
        "mangsir",
        "poush",
        "magh",
        "falgun",
        "chaitra",
    ]
    for relative_path in (
        "data/future_bs/public/official_holdout_2078_2083.csv",
        "data/future_bs/benchmarks/official_holdout_v1.csv",
    ):
        with (root / relative_path).open(encoding="utf-8-sig", newline="") as handle:
            row = next(row for row in csv.DictReader(handle) if int(row["bs_year"]) == 2082)
        assert [int(row[column]) for column in columns] == expected

    normalized = json.loads(
        (root / "data/sources/normalized/calendar/doib_2082_month_lengths.json").read_text(
            encoding="utf-8"
        )
    )
    assert normalized["month_lengths"] == expected
