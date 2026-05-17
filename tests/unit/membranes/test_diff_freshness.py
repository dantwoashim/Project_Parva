from __future__ import annotations

from app.membranes.diff import diff_membrane
from app.membranes.freshness import resolve_freshness


def test_diff_and_freshness_mark_superseded_reports() -> None:
    diff = diff_membrane({"holiday": False}, {"holiday": True}, ["payroll-report-1"])
    freshness = resolve_freshness("old", {"new"}, superseded_by="new")
    assert "holiday" in diff["changed_fields"]
    assert freshness["status"] == "valid_superseded"
