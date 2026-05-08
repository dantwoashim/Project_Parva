from app.future_bs import data_acquisition as da


def test_human_review_queue_prioritizes_conflicts(tmp_path, monkeypatch):
    monkeypatch.setattr(da, "CORPUS_DIR", tmp_path)
    start_rows = [
        {
            "bs_year": 2083,
            "bs_month": 6,
            "month_start_ad": "2026-09-17",
            "source_ids": "official",
            "conflicting_source_ids": "weak",
            "best_source_tier": 1,
            "manual_review_required": "true",
        }
    ]
    length_rows = [
        {
            "bs_year": 2083,
            "bs_month": 6,
            "month_length": 31,
        }
    ]

    rows = da.generate_human_review_queue(start_rows, length_rows)

    assert rows
    assert rows[0]["issue_type"] == "source_disagreement"
    assert int(rows[0]["priority"]) >= 100
