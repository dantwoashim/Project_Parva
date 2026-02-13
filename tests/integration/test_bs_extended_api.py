"""Week 22-24 API integration checks for dual-mode BS confidence."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_bs_to_gregorian_official_confidence():
    response = client.post("/api/calendar/bs-to-gregorian", json={"year": 2080, "month": 1, "day": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["bs"]["confidence"] == "official"
    assert body["bs"]["source_range"] is not None
    assert body["bs"]["estimated_error_days"] is None


def test_bs_to_gregorian_estimated_confidence_for_far_year():
    response = client.post("/api/calendar/bs-to-gregorian", json={"year": 2150, "month": 1, "day": 1})
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


def test_convert_compare_returns_both_modes():
    response = client.get("/api/calendar/convert/compare", params={"date": "2026-02-15"})
    assert response.status_code == 200
    body = response.json()
    assert "official" in body
    assert "estimated" in body
    assert body["estimated"]["confidence"] == "estimated"
