from app.future_bs.sequence.month_start_lattice_decoder import decode_month_start_lattice


def test_month_start_lattice_decoder_marks_invalid_years_non_claimable(tmp_path):
    path = tmp_path / "reconstructed_month_lengths.csv"
    path.write_text(
        "bs_year,bs_month,month_length,verification_status\n"
        + "\n".join(f"2080,{month},30,verified" for month in range(1, 13))
        + "\n",
        encoding="utf-8",
    )
    payload = decode_month_start_lattice(path)
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["year_count"] > 0
    for row in payload["invalid_years"]:
        assert row["risk_label"] == "RED"
        assert row["claimable"] is False
