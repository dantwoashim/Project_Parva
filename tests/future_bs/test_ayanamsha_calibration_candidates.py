from __future__ import annotations

from app.research.future_bs.ayanamsha_calibration import ayanamsha_calibration_summary


def test_ayanamsha_summary_is_marked_as_candidate_registry_not_calibration():
    payload = ayanamsha_calibration_summary()

    assert payload["active"] == "lahiri"
    assert payload["candidates"]
    assert payload["calibration_mode"] == "candidate_registry_not_empirical_calibration"
    assert "registered" in payload["status"]
