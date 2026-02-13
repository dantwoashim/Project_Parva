"""Contract tests for Week 7 response metadata."""

from fastapi.testclient import TestClient

from app.main import app


def _assert_common_headers(response):
    assert response.headers.get("X-Parva-Engine") == "v2"
    assert response.headers.get("X-Parva-Ephemeris")


def test_convert_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/convert", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert body["engine_version"] == "v2"
    assert body["bikram_sambat"]["confidence"] in {"official", "estimated"}
    assert "source_range" in body["bikram_sambat"]
    assert "estimated_error_days" in body["bikram_sambat"]
    assert body["tithi"]["method"] in {"ephemeris_udaya", "instantaneous"}


def test_today_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/today")
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert body["engine_version"] == "v2"
    assert body["tithi"]["method"] in {"ephemeris_udaya", "instantaneous"}
    assert "source_range" in body["bikram_sambat"]
    assert "estimated_error_days" in body["bikram_sambat"]


def test_panchanga_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/panchanga", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert body["engine_version"] == "v2"
    assert body["panchanga"]["confidence"] == "astronomical"
    assert "source_range" in body["bikram_sambat"]
    assert "estimated_error_days" in body["bikram_sambat"]


def test_engine_config_endpoint():
    client = TestClient(app)
    response = client.get("/api/engine/config")
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert set(body.keys()) == {"ayanamsa", "coordinate_system", "ephemeris_mode", "header"}
    assert body["header"] == "moshier-lahiri-sidereal"


def test_convert_compare_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/convert/compare", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert body["engine_version"] == "v2"
    assert "official" in body
    assert "estimated" in body
    assert "match" in body
    assert body["estimated"]["confidence"] == "estimated"
    assert body["estimated"]["estimated_error_days"] == "0-1"
    if body["official"] is not None:
        assert body["official"]["confidence"] == "official"
        assert body["official"]["source_range"] is not None
