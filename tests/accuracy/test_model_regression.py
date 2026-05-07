"""Regression checks for immutable future-BS prediction artifacts."""

from __future__ import annotations

from pathlib import Path

from app.future_bs.models import METHOD_VERSION, MONTH_DAY_VALUES
from app.future_bs.precomputed_store import load_precomputed_predictions

ROOT = Path(__file__).resolve().parents[2]


def test_precomputed_predictions_use_current_method_version_and_valid_month_lengths():
    payload = load_precomputed_predictions()

    assert payload["available"] is True
    assert payload["method_version"] == METHOD_VERSION
    assert payload["years"]
    for year_payload in payload["years"].values():
        assert len(year_payload["months"]) == 12
        assert all(days in MONTH_DAY_VALUES for days in year_payload["months"])


def test_legacy_v3_artifact_is_not_the_active_store():
    prediction_dir = ROOT / "data" / "future_bs" / "predictions"
    active_names = {path.name for path in prediction_dir.glob("*.json")}

    assert any(name.startswith(METHOD_VERSION) for name in active_names)
    assert not any(name.startswith("parva_solar_ingress_de440_calibrated_v3") for name in active_names)
