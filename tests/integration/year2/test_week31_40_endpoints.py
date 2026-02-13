from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_observance_next_endpoint():
    resp = client.get(
        "/v2/api/observances/next",
        params={
            "from_date": "2026-10-01",
            "days": 60,
            "location": "kathmandu",
            "preferences": "nepali_hindu",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "resolved_date" in body
    assert body["top_observance"] is not None


def test_observance_stream_endpoint():
    resp = client.get(
        "/v2/api/observances/stream",
        params={
            "start": "2026-10-20",
            "days": 5,
            "location": "kathmandu",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["days"] == 5
    assert len(body["results"]) == 5
    assert all("date" in row and "observances" in row for row in body["results"])


def test_engine_observance_calculate_route_exists():
    resp = client.get(
        "/v2/api/engine/observance-calculate",
        params={"plugin": "islamic", "rule_id": "eid-al-fitr", "year": 2026, "mode": "announced"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["plugin"] == "islamic"


def test_webhooks_list_endpoint_accessible():
    resp = client.get("/v2/api/webhooks")
    assert resp.status_code == 200
    assert "subscriptions" in resp.json()
