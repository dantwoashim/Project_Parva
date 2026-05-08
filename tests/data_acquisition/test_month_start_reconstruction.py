from app.future_bs import data_acquisition as da


def test_month_start_reconstruction_derives_lengths(tmp_path, monkeypatch):
    monkeypatch.setattr(da, "CORPUS_DIR", tmp_path)
    starts = da.month_start_dates_from_lengths(
        {2080: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30]},
        start_ad=da.date(2023, 4, 14),
        start_bs_year=2080,
    )
    start_rows = []
    for (year, month), ad_start in sorted(starts.items()):
        start_rows.append(
            {
                "bs_year": year,
                "bs_month": month,
                "month_start_ad": ad_start.isoformat(),
                "witness_count": 1,
                "best_source_tier": 1,
                "agreement_score": 1.0,
                "verification_status": "verified",
            }
        )

    rows = da.reconstruct_month_lengths(start_rows)

    assert rows[0]["month_length"] == 31
    assert rows[0]["usable_for_official_claim"] == "true"
