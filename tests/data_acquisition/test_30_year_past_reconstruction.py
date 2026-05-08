import pytest
from app.future_bs import data_acquisition as da


def test_thirty_plus_past_medium_high_years_are_reconstructed():
    metrics = da.coverage_metrics()
    if not metrics["medium_high_30_past_year_subgoal_met"]:
        pytest.skip("private reconstructed medium/high corpus artifact is not present")

    assert metrics["medium_high_30_past_year_subgoal_met"] is True
    assert metrics["medium_high_past_years_with_12_months"] >= 30
    assert len(metrics["medium_high_past_years_with_12_months_list"]) >= 30
    assert max(metrics["medium_high_past_years_with_12_months_list"]) <= 2083


def test_check_data_target_reports_30_year_subgoal():
    result = da.check_data_target()
    if not result["medium_high_30_past_year_subgoal_met"]:
        pytest.skip("private reconstructed medium/high corpus artifact is not present")

    assert result["target_passed"] is True
    assert result["medium_high_30_past_year_subgoal_met"] is True
    assert result["medium_high_past_years_with_12_months"] >= 30
