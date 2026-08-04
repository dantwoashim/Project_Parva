from __future__ import annotations

import csv
from pathlib import Path


def test_ird_vendor_prospect_set_is_complete_and_deduplicated() -> None:
    root = Path(__file__).resolve().parents[2]
    path = root / "docs" / "outreach" / "ird_vendor_prospects_2026.csv"

    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 50
    assert [int(row["rank"]) for row in rows] == list(range(1, 51))
    assert len({row["pan"] for row in rows}) == 50
    assert {row["priority"] for row in rows} == {"A", "B"}
    assert all(row["application_name"] for row in rows)
    assert all(row["enlisted_no"].isdigit() for row in rows)
    assert all(row["fit_reason"] and row["outreach_angle"] for row in rows)
