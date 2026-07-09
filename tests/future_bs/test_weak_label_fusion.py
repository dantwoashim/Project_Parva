from app.research.future_bs.truth_fusion.weak_label_fusion import fuse_month_start_candidates


def test_weak_label_fusion_produces_posteriors():
    payload = fuse_month_start_candidates(
        {
            "nodes": {
                "2080-01": {
                    "bs_year": 2080,
                    "bs_month": 1,
                    "chosen_month_start_ad": "2023-04-14",
                    "conflict": False,
                    "candidates": [
                        {
                            "month_start_ad": "2023-04-14",
                            "weight": 1.0,
                            "source_ids": ["official_verified_sample"],
                        }
                    ],
                }
            }
        }
    )
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["case_count"] > 0
    first = next(iter(payload["results"].values()))
    probs = [row["posterior_probability"] for row in first["posterior_candidates"]]
    assert probs
    assert abs(sum(probs) - 1.0) < 0.01
