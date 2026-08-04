from __future__ import annotations

import json
from pathlib import Path

import pytest
from app.services.future_bs_public_service import (
    future_bs_forecast_payload,
    future_bs_methodology_payload,
)

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "data" / "future_bs" / "public" / "forecast_snapshot_v6_2084_2200.json"


def test_public_snapshot_covers_the_declared_range_with_valid_years() -> None:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert payload["publication_status"] == "computed_prediction_not_official"
    assert sorted(int(year) for year in payload["years"]) == list(range(2084, 2201))
    for year, forecast in payload["years"].items():
        assert len(forecast["month_lengths"]) == 12, year
        assert len(forecast["months"]) == 12, year
        assert sum(forecast["month_lengths"]) in {365, 366}, year
        assert all(29 <= days <= 32 for days in forecast["month_lengths"]), year


def test_public_forecast_exposes_selected_output_without_raw_research_payloads() -> None:
    forecast = future_bs_forecast_payload(2084, trace_id="test-trace")

    assert forecast["publication_status"] == "computed_prediction_not_official"
    assert forecast["review_required"] is True
    assert forecast["meta"]["source"]["tier"] == "calculated"
    assert forecast["meta"]["trace_id"] == "test-trace"
    assert forecast["risk_summary"] == {"GREEN": 0, "YELLOW": 12, "RED": 0}
    assert "computational_model_outputs" not in forecast
    assert "legacy_model_output" not in forecast


def test_public_methodology_labels_the_72_case_result_as_replay() -> None:
    methodology = future_bs_methodology_payload()
    validation = methodology["validation"]

    assert validation["official_window_replay"]["exact_month_matches"] == 72
    assert validation["official_window_replay"]["month_cases"] == 72
    assert validation["official_window_replay"]["evaluation_kind"] == "calibrated_official_window_replay"
    assert validation["independent_broad_accuracy_claim_ready"] is False


def test_public_forecast_rejects_years_outside_the_snapshot() -> None:
    with pytest.raises(ValueError, match="2084-2200"):
        future_bs_forecast_payload(2201)
