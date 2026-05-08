from app.future_bs.sequence.month_start_lattice_decoder import decode_month_start_lattice


def test_month_start_lattice_decoder_marks_invalid_years_non_claimable():
    payload = decode_month_start_lattice()
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["year_count"] > 0
    for row in payload["invalid_years"]:
        assert row["risk_label"] == "RED"
        assert row["claimable"] is False
