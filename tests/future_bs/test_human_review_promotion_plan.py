from app.future_bs.active_learning.promotion_plan import build_human_review_promotion_plan


def test_human_review_promotion_plan_has_top_rows():
    rows = build_human_review_promotion_plan()
    assert len(rows) == 100
    assert rows[0]["rank"] == 1
    assert rows[0]["recommended_manual_action"]
