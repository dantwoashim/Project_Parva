from app.research.future_bs import data_acquisition as da


def test_data_target_checker_fails_when_reconstruction_is_insufficient(monkeypatch):
    monkeypatch.setattr(
        da,
        "coverage_metrics",
        lambda: {
            "primary_target_met": False,
            "minimum_fallback_met": False,
            "medium_high_subgoal_met": False,
            "years_with_12_months": 1,
            "months_reconstructed": 12,
        },
    )

    result = da.check_data_target()

    assert result["target_passed"] is False
    assert "minimum_fallback_not_met" in result["blockers"]


def test_data_target_checker_passes_with_generated_corpus(monkeypatch):
    monkeypatch.setattr(
        da,
        "coverage_metrics",
        lambda: {
            "primary_target_met": True,
            "minimum_fallback_met": True,
            "medium_high_subgoal_met": True,
            "medium_high_30_past_year_subgoal_met": True,
            "medium_high_past_years_with_12_months": 40,
            "medium_high_past_years_with_12_months_list": list(range(2044, 2084)),
            "years_with_12_months": 40,
            "months_reconstructed": 480,
        },
    )

    result = da.check_data_target()

    assert result["target_passed"] is True
    assert result["months_reconstructed"] >= 480
