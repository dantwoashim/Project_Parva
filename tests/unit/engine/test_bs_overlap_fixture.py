"""BS overlap fixture regression checks (Week 21)."""

from __future__ import annotations

import json
from pathlib import Path


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "bs_overlap_comparison.json"


def test_bs_overlap_fixture_exists_and_has_expected_window():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    meta = data["metadata"]

    assert meta["official_bs_range"] == "2070-2095"
    assert meta["total_days"] >= 9000
    assert len(data["rows"]) == meta["total_days"]


def test_bs_overlap_match_rate_consistent_with_rows():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rows = data["rows"]
    meta = data["metadata"]

    matches = sum(1 for row in rows if row["match"])
    mismatches = len(rows) - matches

    assert matches == meta["matches"]
    assert mismatches == meta["mismatches"]
    assert mismatches > 0
