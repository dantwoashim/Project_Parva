from __future__ import annotations

from datetime import date

from app.services.calendar_surface_service import (
    build_panchanga_payload,
    build_tithi_detail_payload,
)


def test_tithi_detail_strict_mode_abstains_near_boundary(monkeypatch):
    import app.calendar.tithi as tithi_module
    import app.calendar.tithi.tithi_udaya as udaya_module

    monkeypatch.setattr(
        tithi_module,
        "get_udaya_tithi",
        lambda target_date, latitude=None, longitude=None: {
            "sunrise_local": __import__("datetime").datetime(2026, 2, 15, 6, 20),
            "tithi_absolute": 29,
            "tithi": 14,
            "paksha": "krishna",
            "name": "Chaturdashi",
            "progress": 0.98,
        },
    )
    monkeypatch.setattr(tithi_module, "get_moon_phase_name", lambda *_args, **_kwargs: "waning")
    monkeypatch.setattr(udaya_module, "detect_vriddhi", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(udaya_module, "detect_ksheepana", lambda *_args, **_kwargs: False)

    payload = build_tithi_detail_payload(
        date(2026, 2, 15),
        latitude=27.7172,
        longitude=85.3240,
        risk_mode="strict",
    )

    assert payload["boundary_radar"] == "high_disagreement_risk"
    assert payload["risk_mode"] == "strict"
    assert payload["abstained"] is True
    assert payload["stability_score"] < 0.8
    assert payload["recommended_action"]


def test_panchanga_strict_mode_abstains_near_boundary(monkeypatch):
    import app.calendar.panchanga as panchanga_module

    monkeypatch.setattr(
        panchanga_module,
        "get_panchanga",
        lambda target_date: {
            "tithi": {"number": 14, "name": "Chaturdashi", "paksha": "krishna", "progress": 0.02},
            "nakshatra": {"number": 10, "name": "Magha", "pada": 1},
            "yoga": {"number": 5, "name": "Saubhagya"},
            "karana": {"number": 6, "name": "Taitila"},
            "vaara": {"name_sanskrit": "Ravivara", "name_english": "Sunday"},
            "sunrise": {"local": "2026-02-15T06:42:00+05:45"},
            "mode": "swiss_moshier",
            "accuracy": "arcsecond",
            "library": "pyswisseph",
        },
    )

    payload = build_panchanga_payload(date(2026, 2, 15), risk_mode="strict")

    assert payload["boundary_radar"] == "high_disagreement_risk"
    assert payload["risk_mode"] == "strict"
    assert payload["abstained"] is True
    assert payload["stability_score"] < 0.8
    assert payload["recommended_action"]
