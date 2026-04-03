from __future__ import annotations

from app.reliability import get_differential_manifest


def test_differential_manifest_exposes_drift_summary():
    payload = get_differential_manifest()

    assert payload["total_compared"] >= 1
    assert payload["drift_percent"] >= 0.0
    assert isinstance(payload["taxonomy"], dict)
    assert "agreement" in payload["taxonomy"]
    assert isinstance(payload["sample_details"], list)
