from app.future_bs.truth_fusion.latent_truth_model import infer_latent_truth


def test_latent_truth_model_marks_review_cases():
    payload = infer_latent_truth()
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["case_count"] > 0
    assert payload["manual_review_required_count"] >= 0
