"""Regression checks for immutable future-BS prediction artifacts."""

from __future__ import annotations

import subprocess

from app.future_bs.models import METHOD_VERSION, MONTH_DAY_VALUES
from app.future_bs.precomputed_store import load_precomputed_predictions


def _load_available_predictions():
    payload = load_precomputed_predictions()
    if not payload.get("available"):
        subprocess.run(["python", "scripts/future_bs/run_accuracy_loop.py", "--final"], check=True)
        load_precomputed_predictions.cache_clear()
        payload = load_precomputed_predictions()
    return payload


def test_precomputed_predictions_use_current_method_version_and_valid_month_lengths():
    payload = _load_available_predictions()

    assert payload["available"] is True
    assert payload["method_version"] == METHOD_VERSION
    assert payload["years"]
    for year_payload in payload["years"].values():
        assert len(year_payload["months"]) == 12
        assert all(days in MONTH_DAY_VALUES for days in year_payload["months"])


def test_legacy_v3_artifact_is_not_the_active_store():
    payload = _load_available_predictions()

    assert payload["method_version"] == METHOD_VERSION
    assert payload.get("run_id") != "parva_solar_ingress_de440_calibrated_v3"
