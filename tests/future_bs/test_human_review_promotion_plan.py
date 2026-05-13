import csv

from app.future_bs.active_learning import promotion_plan


def test_human_review_promotion_plan_has_top_rows(tmp_path, monkeypatch):
    review_path = tmp_path / "human_review_queue.csv"
    lab_dir = tmp_path / "lab"
    fields = [
        "priority",
        "bs_year",
        "bs_month",
        "issue_type",
        "sources",
        "reason",
        "recommended_manual_action",
        "source_file_or_url",
        "page_number_or_crop_if_available",
    ]
    with review_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for index in range(100):
            writer.writerow(
                {
                    "priority": 100 - index % 10,
                    "bs_year": 2076 + index % 8,
                    "bs_month": index % 12 + 1,
                    "issue_type": "source_disagreement",
                    "sources": "official;printed",
                    "reason": "conflict needs review",
                    "recommended_manual_action": "Verify printed or official month-start witness.",
                    "source_file_or_url": "sample",
                    "page_number_or_crop_if_available": "",
                }
            )
    monkeypatch.setattr(promotion_plan, "REVIEW_PATH", review_path)
    monkeypatch.setattr(promotion_plan, "LAB_DIR", lab_dir)

    rows = promotion_plan.build_human_review_promotion_plan()
    assert len(rows) == 100
    assert rows[0]["rank"] == 1
    assert rows[0]["recommended_manual_action"]
    assert not (lab_dir / "human_review_promotion_plan.csv").exists()

    paths = promotion_plan.write_human_review_promotion_plan(rows, output_dir=lab_dir)
    assert paths["csv"].exists()
    assert paths["markdown"].exists()
