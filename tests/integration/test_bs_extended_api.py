"""Week 22-24 API integration checks for dual-mode BS confidence."""

from datetime import date

import app.services.calendar_surface_service as calendar_surface_service
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_bs_to_gregorian_official_confidence():
    response = client.post(
        "/api/calendar/bs-to-gregorian", json={"year": 2080, "month": 1, "day": 1}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["bs"]["confidence"] == "official"
    assert body["bs"]["source_range"] is not None
    assert body["bs"]["estimated_error_days"] is None


def test_bs_to_gregorian_estimated_confidence_for_far_year():
    response = client.post(
        "/api/calendar/bs-to-gregorian", json={"year": 2150, "month": 1, "day": 1}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["bs"]["confidence"] == "estimated"
    assert body["bs"]["source_range"] is None
    assert body["bs"]["estimated_error_days"] == "0-1"


def test_convert_includes_estimated_error_metadata_for_out_of_range_date():
    response = client.get("/api/calendar/convert", params={"date": "2050-02-15"})
    assert response.status_code == 200
    body = response.json()
    assert body["bikram_sambat"]["confidence"] == "estimated"
    assert body["bikram_sambat"]["estimated_error_days"] == "0-1"


def test_convert_uses_correct_2081_bhadra_boundary():
    response = client.get("/api/calendar/convert", params={"date": "2024-08-21"})
    assert response.status_code == 200
    body = response.json()
    assert body["bikram_sambat"]["year"] == 2081
    assert body["bikram_sambat"]["month"] == 5
    assert body["bikram_sambat"]["day"] == 5
    assert body["bikram_sambat"]["month_name"] == "Bhadra"


def test_convert_uses_correct_2082_ashwin_boundary():
    response = client.get("/api/calendar/convert", params={"date": "2025-10-17"})
    assert response.status_code == 200
    body = response.json()
    assert body["bikram_sambat"]["year"] == 2082
    assert body["bikram_sambat"]["month"] == 6
    assert body["bikram_sambat"]["day"] == 31
    assert body["bikram_sambat"]["month_name"] == "Ashwin"


def test_today_exposes_nepal_civil_weekday(monkeypatch):
    monkeypatch.setattr(calendar_surface_service, "_nepal_today", lambda: date(2026, 4, 30))

    response = client.get("/api/calendar/today")
    assert response.status_code == 200
    body = response.json()
    assert body["gregorian"] == "2026-04-30"
    assert body["weekday"]["name_english"] == "Thursday"
    assert body["weekday"]["name_sanskrit"] == "Guruvara"
    assert body["tithi"]["sunrise_used"].startswith("2026-04-30")


def test_convert_tithi_uses_nepal_civil_sunrise():
    response = client.get("/api/calendar/convert", params={"date": "2026-04-30"})
    assert response.status_code == 200
    body = response.json()
    assert body["tithi"]["tithi_name"] == "Chaturdashi"
    assert body["tithi"]["sunrise_used"].startswith("2026-04-30")


def test_panchanga_uses_nepal_civil_weekday_and_sunrise():
    response = client.get("/api/calendar/panchanga", params={"date": "2026-04-30"})
    assert response.status_code == 200
    body = response.json()
    assert body["panchanga"]["vaara"]["name_english"] == "Thursday"
    assert body["panchanga"]["tithi"]["name"] == "Chaturdashi"
    assert body["panchanga"]["tithi"]["sunrise_used"].startswith("2026-04-30")


def test_convert_compare_returns_both_modes():
    response = client.get("/api/calendar/convert/compare", params={"date": "2026-02-15"})
    assert response.status_code == 200
    body = response.json()
    assert "official" in body
    assert "estimated" in body
    assert body["estimated"]["confidence"] == "estimated"
