from app.research.future_bs.truth_fusion.latent_truth_model import infer_latent_truth


def test_latent_truth_model_marks_review_cases():
    payload = infer_latent_truth(
        {
            "results": {
                "2080-01": {
                    "bs_year": 2080,
                    "bs_month": 1,
                    "conflict": False,
                    "selected_month_start_ad": "2023-04-14",
                    "posterior_candidates": [
                        {
                            "month_start_ad": "2023-04-14",
                            "posterior_probability": 0.92,
                        }
                    ],
                }
            }
        }
    )
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["algorithm_claim"] == "consensus_selector_not_bayesian_latent_variable_model"
    assert payload["method"] == "reliability_weighted_consensus_selector_v1"
    assert payload["case_count"] > 0
    assert payload["manual_review_required_count"] >= 0
