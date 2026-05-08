from app.future_bs.truth_fusion.weak_label_fusion import fuse_month_start_candidates


def test_weak_label_fusion_produces_posteriors():
    payload = fuse_month_start_candidates()
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["case_count"] > 0
    first = next(iter(payload["results"].values()))
    probs = [row["posterior_probability"] for row in first["posterior_candidates"]]
    assert probs
    assert abs(sum(probs) - 1.0) < 0.01
