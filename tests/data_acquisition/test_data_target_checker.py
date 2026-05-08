from pathlib import Path

from app.future_bs import data_acquisition as da


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


def test_data_target_checker_passes_with_generated_corpus():
    assert Path("data/future_bs/witnesses/extracted_witnesses.csv").stat().st_size > 0
    assert Path("data/future_bs/corpus/reconstructed_month_lengths.csv").stat().st_size > 0

    result = da.check_data_target()

    assert result["target_passed"] is True
    assert result["months_reconstructed"] >= 480
