"""Strict future-year total gate tests."""

from app.research.future_bs.year_total_gate import apply_year_total_gate, year_total_gate


def test_year_total_gate_accepts_normal_future_totals():
    assert year_total_gate([30] * 7 + [31] * 5)["valid_future_year_total"] is True


def test_year_total_gate_marks_exceptional_total_red():
    payload = apply_year_total_gate(
        {
            "months": [30] * 12,
            "risk_flags": [],
            "month_details": [{"risk_flags": [], "confidence_label": "computed_medium"}],
        }
    )

    assert payload["year_total_gate"]["risk_label"] == "RED"
    assert payload["year_total_gate"]["claimable"] is False
    assert "invalid_or_exceptional_year_total" in payload["risk_flags"]
