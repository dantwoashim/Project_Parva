from __future__ import annotations

from app.disagreement.convergence import convergence_report
from app.reports.skeptic import render_skeptic_report


def test_skeptic_report_shows_conflict_status() -> None:
    branches = [
        {"branch_id": "canonical", "result": {"date": "a"}, "boundary": {"authority": "computed_uncertified"}},
        {"branch_id": "community", "result": {"date": "b"}, "boundary": {"authority": "community_specific"}},
    ]
    assert convergence_report(branches)["conflict_status"] == "conflicted"
    assert "Conflict status" in render_skeptic_report(branches)
