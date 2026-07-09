from app.research.future_bs.regime.regime_model import detect_regime_changes


def test_regime_change_detection_assigns_regimes():
    payload = detect_regime_changes(
        {
            "features": [
                {
                    "bs_year": 2078,
                    "bs_month": 1,
                    "best_source_tier": 1,
                    "agreement_score": 1.0,
                    "boundary_sensitive_month": True,
                },
                {
                    "bs_year": 2050,
                    "bs_month": 1,
                    "best_source_tier": 4,
                    "agreement_score": 0.8,
                    "boundary_sensitive_month": False,
                },
            ]
        }
    )
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["regime_counts"]
    assert payload["assignments"]
