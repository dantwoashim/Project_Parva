from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_personal_panchanga_v3_fields():
    resp = client.get("/v3/api/personal/panchanga", params={"date": "2026-02-15"})
    assert resp.status_code == 200
    body = resp.json()
    assert "bikram_sambat" in body
    assert "tithi" in body
    assert "nakshatra" in body
    assert "yoga" in body
    assert "karana" in body
    assert "vaara" in body
    assert "calculation_trace_id" in body
    assert body["method_profile"] == "personal_panchanga_v2_udaya"
    assert body["quality_band"] in {"validated", "gold"}
    assert body["assumption_set_id"]
    assert body["advisory_scope"] == "ritual_planning"


def test_personal_panchanga_post_hides_inputs_from_url_and_disables_caching():
    resp = client.post(
        "/v3/api/personal/panchanga",
        json={"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"},
    )
    assert resp.status_code == 200
    assert resp.request.url.query == b""
    assert resp.headers["Cache-Control"] == "no-store"


def test_personal_panchanga_post_accepts_numeric_coordinates():
    resp = client.post(
        "/v3/api/personal/panchanga",
        json={"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240},
    )
    assert resp.status_code == 200
    assert resp.json()["location"] == {
        "latitude": 27.7172,
        "longitude": 85.324,
        "timezone": "Asia/Kathmandu",
    }


def test_personal_panchanga_get_and_post_normalize_coordinates_equivalently():
    params = {"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"}
    payload = {"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240}

    get_resp = client.get("/v3/api/personal/panchanga", params=params)
    post_resp = client.post("/v3/api/personal/panchanga", json=payload)

    assert get_resp.status_code == 200
    assert post_resp.status_code == 200

    get_body = get_resp.json()
    post_body = post_resp.json()
    assert get_body["location"] == post_body["location"]
    assert get_body["bikram_sambat"] == post_body["bikram_sambat"]
    assert get_body["tithi"] == post_body["tithi"]


def test_muhurta_returns_named_slots():
    resp = client.get("/v3/api/muhurta", params={"date": "2026-02-15"})
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body.get("muhurtas"), list)
    assert len(body["muhurtas"]) == 30
    assert body["muhurtas"][0]["name"]
    assert body["muhurtas"][0]["duration_minutes"] > 0
    assert len(body["day_muhurtas"]) == 15
    assert len(body["night_muhurtas"]) == 15
    assert len(body["hora"]["day"]) == 12
    assert len(body["hora"]["night"]) == 12
    assert len(body["chaughadia"]["day"]) == 8
    assert len(body["chaughadia"]["night"]) == 8
    assert "tara_bala" in body
    assert body["method_profile"] == "muhurta_v2_hora_chaughadia_tarabala"
    assert body["quality_band"] in {"beta", "validated", "gold"}


def test_muhurta_heatmap_post_supported_for_private_inputs():
    resp = client.post(
        "/v3/api/muhurta/heatmap",
        json={"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"},
    )
    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "no-store"


def test_muhurta_heatmap_post_accepts_numeric_coordinates():
    resp = client.post(
        "/v3/api/muhurta/heatmap",
        json={"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240},
    )
    assert resp.status_code == 200
    assert resp.json()["best_window"]["name"]


def test_muhurta_heatmap_get_and_post_normalize_coordinates_equivalently():
    params = {"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"}
    payload = {"date": "2026-02-15", "lat": 27.7172, "lon": 85.3240}

    get_resp = client.get("/v3/api/muhurta/heatmap", params=params)
    post_resp = client.post("/v3/api/muhurta/heatmap", json=payload)

    assert get_resp.status_code == 200
    assert post_resp.status_code == 200

    get_body = get_resp.json()
    post_body = post_resp.json()
    assert get_body["best_window"] == post_body["best_window"]
    assert get_body["blocks"] == post_body["blocks"]


def test_rahu_kalam_changes_by_weekday():
    sunday = client.get("/v3/api/muhurta/rahu-kalam", params={"date": "2026-02-15"})
    monday = client.get("/v3/api/muhurta/rahu-kalam", params={"date": "2026-02-16"})
    assert sunday.status_code == 200
    assert monday.status_code == 200
    assert sunday.json()["rahu_kalam"]["segment"] != monday.json()["rahu_kalam"]["segment"]


def test_muhurta_auspicious_ranked_output():
    resp = client.get(
        "/v3/api/muhurta/auspicious",
        params={
            "date": "2026-02-15",
            "type": "vivah",
            "birth_nakshatra": "7",
            "assumption_set": "np-mainstream-v2",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["method_profile"] == "muhurta_v2_hora_chaughadia_tarabala"
    assert body["assumption_set_id"] == "np-mainstream-v2"
    assert isinstance(body.get("ranked_muhurtas"), list)
    assert body["best_window"]["score"] >= body["ranked_muhurtas"][-1]["score"]
    assert "tara_bala" in body


def test_kundali_returns_12_houses_and_navagraha():
    resp = client.get(
        "/v3/api/kundali",
        params={"datetime": "2026-02-15T06:30:00+05:45", "lat": "27.7172", "lon": "85.3240"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body.get("houses", [])) == 12
    assert len(body.get("grahas", {})) == 9
    assert "dasha" in body
    assert isinstance(body.get("aspects"), list)
    assert isinstance(body.get("yogas"), list)
    assert isinstance(body.get("doshas"), list)
    assert isinstance(body.get("consistency_checks"), list)
    assert body["dasha"]["total_major_periods"] == 9
    assert len(body["dasha"]["timeline"][0]["antar_dasha"]) == 9
    assert body["method_profile"] == "kundali_v2_aspects_dasha"
    assert body["assumption_set_id"] == "np-kundali-v2"
    assert body["quality_band"] in {"validated", "gold"}
    assert body["advisory_scope"] == "astrology_assist"


def test_kundali_post_supported_for_private_inputs():
    resp = client.post(
        "/v3/api/kundali",
        json={"datetime": "2026-02-15T06:30:00+05:45", "lat": "27.7172", "lon": "85.3240"},
    )
    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "no-store"


def test_kundali_post_accepts_numeric_coordinates():
    resp = client.post(
        "/v3/api/kundali",
        json={"datetime": "2026-02-15T06:30:00+05:45", "lat": 27.7172, "lon": 85.3240},
    )
    assert resp.status_code == 200
    assert resp.json()["location"] == {
        "latitude": 27.7172,
        "longitude": 85.324,
        "timezone": "Asia/Kathmandu",
    }


def test_kundali_get_and_post_normalize_coordinates_equivalently():
    params = {"datetime": "2026-02-15T06:30:00+05:45", "lat": "27.7172", "lon": "85.3240"}
    payload = {"datetime": "2026-02-15T06:30:00+05:45", "lat": 27.7172, "lon": 85.3240}

    get_resp = client.get("/v3/api/kundali", params=params)
    post_resp = client.post("/v3/api/kundali", json=payload)

    assert get_resp.status_code == 200
    assert post_resp.status_code == 200

    get_body = get_resp.json()
    post_body = post_resp.json()
    assert get_body["location"] == post_body["location"]
    assert get_body["lagna"] == post_body["lagna"]
    assert get_body["houses"] == post_body["houses"]


def test_kundali_invalid_datetime_returns_400():
    resp = client.get("/v3/api/kundali", params={"datetime": "not-a-datetime"})
    assert resp.status_code == 400


def test_invalid_coordinates_return_400():
    get_resp = client.get("/v3/api/muhurta", params={"date": "2026-02-15", "lat": "999", "lon": "85.3240"})
    post_resp = client.post(
        "/v3/api/muhurta/heatmap",
        json={"date": "2026-02-15", "lat": 27.7172, "lon": 999},
    )

    assert get_resp.status_code == 400
    assert post_resp.status_code == 400
    assert "Out-of-range lat" in get_resp.json()["detail"]
    assert "Out-of-range lon" in post_resp.json()["detail"]
