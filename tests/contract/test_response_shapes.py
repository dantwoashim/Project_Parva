from app.main import app
from fastapi.testclient import TestClient


def _assert_common_headers(response):
    assert response.headers.get("X-Parva-Engine") == "v3"
    assert response.headers.get("X-Parva-Ephemeris")
    assert response.headers.get("X-Parva-License") == "AGPL-3.0-or-later"


def test_convert_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/convert", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "bikram_sambat" in body
    assert "tithi" in body
    assert body["support_tier"] in {"computed", "estimated", "heuristic"}
    assert body["engine_path"] in {"ephemeris_udaya", "instantaneous"}
    assert isinstance(body["fallback_used"], bool)
    assert body["calibration_status"] == "unavailable"
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
    assert body["support_tier"] in {"computed", "estimated", "heuristic"}
    assert body["engine_path"] in {"ephemeris_udaya", "instantaneous"}
    assert isinstance(body["fallback_used"], bool)
    assert body["calibration_status"] == "unavailable"
    assert body["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert body["risk_mode"] == "standard"
    assert isinstance(body["stability_score"], float)
    assert body["recommended_action"]


def test_panchanga_contract_fields():
    client = TestClient(app)
    response = client.get("/api/calendar/panchanga", params={"date": "2026-02-15"})
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "panchanga" in body
    assert "ephemeris" in body
    assert body["support_tier"] in {"computed", "heuristic"}
    assert body["engine_path"] == "ephemeris_udaya"
    assert body["fallback_used"] is False
    assert body["calibration_status"] == "unavailable"
    assert body["boundary_radar"] in {"stable", "one_day_sensitive", "high_disagreement_risk"}
    assert body["risk_mode"] == "standard"
    assert isinstance(body["stability_score"], float)
    assert body["recommended_action"]
    assert body["panchanga"]["tithi"]["method"] in {"ephemeris_udaya", "instantaneous"}


def test_engine_config_endpoint():
    client = TestClient(app)
    response = client.get("/api/engine/config")
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert "ephemeris_mode" in body
    assert "ayanamsa" in body
    assert body["canonical_engine_id"] == "parva-v3-canonical"
    assert body["manifest_version"] == "2026-03-20"


def test_engine_manifest_endpoint():
    client = TestClient(app)
    response = client.get("/api/engine/manifest")
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert body["canonical_engine_id"] == "parva-v3-canonical"
    assert body["manifest_version"] == "2026-03-20"
    assert body["engine_version"] == "v3"
    assert "public_route_families" in body
    assert len(body["public_route_families"]) >= 3


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
    assert body["support_tier"] in {"computed", "estimated"}
    assert body["engine_path"] == "bs_compare_official_vs_estimated"
    assert isinstance(body["fallback_used"], bool)
    assert body["calibration_status"] == "unavailable"


def test_festival_timeline_accepts_upcoming_sort_alias():
    client = TestClient(app)
    response = client.get(
        "/v3/api/festivals/timeline",
        params={
            "from": "2026-03-21",
            "to": "2026-09-16",
            "quality_band": "computed",
            "lang": "en",
            "sort": "upcoming",
        },
    )
    assert response.status_code == 200
    _assert_common_headers(response)

    body = response.json()
    assert body["sort"] == "chronological"
    assert "groups" in body
