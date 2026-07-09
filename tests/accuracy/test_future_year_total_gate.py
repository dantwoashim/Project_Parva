"""Accuracy-level guard for invalid future year totals."""

from app.research.future_bs.year_total_gate import year_total_gate


def test_invalid_future_year_total_is_never_claimable():
    gate = year_total_gate([31] * 12)

    assert gate["valid_future_year_total"] is False
    assert gate["risk_label"] == "RED"
    assert gate["claimable"] is False
    assert gate["manual_review_required"] is True
