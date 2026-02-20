from fastapi.testclient import TestClient

from app.main import app


def _assert_common_headers(response):
    assert response.headers.get("X-Parva-Engine") == "v3"
    assert response.headers.get("X-Parva-Ephemeris")


def test_convert_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/convert", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "bikram_sambat" in body
    assert "tithi" in body
    assert "engine_version" in body
    assert body["engine_version"] in {"v2", "v3"}


def test_today_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/today")
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "gregorian" in body
    assert "bikram_sambat" in body
    assert "tithi" in body


def test_panchanga_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/panchanga", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "panchanga" in body
    assert "ephemeris" in body
    assert body["panchanga"]["tithi"]["method"] in {"ephemeris_udaya", "instantaneous"}


def test_engine_config_endpoint():
    client = TestClient(app)
    response = client.get("/api/engine/config")
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "ephemeris_mode" in body
    assert "ayanamsa" in body


def test_convert_compare_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/convert/compare", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "gregorian" in body
    assert "official" in body
    assert "estimated" in body
    assert "match" in body
