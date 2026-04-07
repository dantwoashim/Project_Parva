from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app, client=("v3-envelope-opt-in-tests", 50000))
ENVELOPE_HEADERS = {"X-Parva-Envelope": "data-meta"}


def _assert_envelope(response):
    assert response.status_code == 200
    assert response.headers["X-Parva-Envelope"] == "data-meta"
    assert "X-Parva-Envelope" in response.headers.get("Vary", "")
    body = response.json()
    assert set(body.keys()) == {"data", "meta"}
    assert isinstance(body["data"], dict)
    assert isinstance(body["meta"], dict)
    return body


def test_v3_default_personal_panchanga_response_remains_flat_without_opt_in():
    response = client.get("/v3/api/personal/panchanga", params={"date": "2026-02-15"})

    assert response.status_code == 200
    body = response.json()
    assert "data" not in body
    assert "meta" not in body
    assert "tithi" in body


def test_v3_personal_panchanga_envelope_opt_in_returns_authoritative_meta():
    response = client.get(
        "/v3/api/personal/panchanga",
        params={"date": "2026-02-15"},
        headers=ENVELOPE_HEADERS,
    )

    body = _assert_envelope(response)
    assert body["data"]["tithi"]["name"]
    assert body["meta"]["trace_id"] == body["data"]["calculation_trace_id"]
    assert body["meta"]["method"] == "ephemeris_udaya"
    assert body["meta"]["policy"]["usage"] == "informational"
    assert body["meta"]["degraded"]["active"] is True


def test_v3_temporal_compass_envelope_opt_in_returns_authoritative_meta():
    response = client.post(
        "/v3/api/temporal/compass",
        json={"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"},
        headers=ENVELOPE_HEADERS,
    )

    body = _assert_envelope(response)
    assert body["data"]["primary_readout"]["tithi_name"]
    assert body["meta"]["trace_id"] == body["data"]["calculation_trace_id"]
    assert body["meta"]["method"] == "ephemeris_udaya"


def test_v3_festival_timeline_envelope_opt_in_returns_authoritative_meta():
    response = client.get(
        "/v3/api/festivals/timeline",
        params={
            "from": "2026-09-01",
            "to": "2026-12-01",
            "quality_band": "all",
            "search": "dashain",
        },
        headers=ENVELOPE_HEADERS,
    )

    body = _assert_envelope(response)
    assert isinstance(body["data"]["groups"], list)
    assert body["meta"]["trace_id"] == body["data"]["calculation_trace_id"]
    assert body["meta"]["method"] == "festival_timeline_grouping"


def test_v3_festival_detail_envelope_opt_in_returns_authoritative_meta():
    response = client.get(
        "/v3/api/festivals/dashain",
        params={"year": 2026},
        headers=ENVELOPE_HEADERS,
    )

    body = _assert_envelope(response)
    assert body["data"]["festival"]["id"] == "dashain"
    assert body["data"]["completeness"]["overall"] in {"complete", "partial", "minimal"}
    assert body["meta"]["provenance"]["verify_url"]
    assert body["meta"]["confidence"] == "unknown"


def test_v3_muhurta_heatmap_envelope_opt_in_returns_authoritative_meta():
    response = client.post(
        "/v3/api/muhurta/heatmap",
        json={"date": "2026-02-15", "lat": "27.7172", "lon": "85.3240"},
        headers=ENVELOPE_HEADERS,
    )

    body = _assert_envelope(response)
    assert isinstance(body["data"]["blocks"], list)
    assert body["meta"]["trace_id"] == body["data"]["calculation_trace_id"]
    assert body["meta"]["method"] == "rule_ranked_muhurta_v2"


def test_v3_kundali_graph_envelope_opt_in_returns_authoritative_meta():
    response = client.post(
        "/v3/api/kundali/graph",
        json={
            "datetime": "2026-02-15T06:30:00+05:45",
            "lat": "27.7172",
            "lon": "85.3240",
        },
        headers=ENVELOPE_HEADERS,
    )

    body = _assert_envelope(response)
    assert body["data"]["layout"]["house_nodes"]
    assert body["meta"]["trace_id"] == body["data"]["calculation_trace_id"]
    assert body["meta"]["method"] == "swiss_ephemeris_sidereal"
