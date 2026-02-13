from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_webhook_store(tmp_path, monkeypatch):
    from app.api import webhook_routes
    from app.integrations.webhooks import WebhookService

    test_store = tmp_path / "subscriptions.json"
    service = WebhookService(store_path=test_store)
    monkeypatch.setattr(webhook_routes, "_service", service)
    yield


def test_observances_resolver_endpoints():
    resp = client.get(
        "/v2/api/observances",
        params={"date": "2026-10-21", "location": "kathmandu", "preferences": "nepali_hindu"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["date"] == "2026-10-21"
    assert isinstance(body["observances"], list)
    assert "has_conflicts" in body

    conflicts = client.get("/v2/api/observances/conflicts")
    assert conflicts.status_code == 200
    payload = conflicts.json()
    assert isinstance(payload.get("scenarios"), list)
    assert payload["scenarios"]


def test_feed_endpoints_emit_ics():
    resp = client.get(
        "/v2/api/feeds/ical",
        params={"festivals": "dashain,tihar", "years": 1, "start_year": 2026, "lang": "en"},
    )
    assert resp.status_code == 200
    assert "text/calendar" in resp.headers.get("content-type", "")
    assert "BEGIN:VCALENDAR" in resp.text
    assert "BEGIN:VEVENT" in resp.text

    national = client.get("/v2/api/feeds/national.ics", params={"years": 1, "start_year": 2026})
    assert national.status_code == 200
    assert "BEGIN:VCALENDAR" in national.text


def test_webhook_subscribe_dispatch_and_dedupe():
    create = client.post(
        "/v2/api/webhooks/subscribe",
        json={
            "subscriber_url": "mock://success",
            "festivals": ["dashain"],
            "remind_days_before": [0],
            "format": "json",
            "active": True,
        },
    )
    assert create.status_code == 200
    sub_id = create.json()["subscription"]["id"]

    dashain = client.get("/v2/api/festivals/dashain", params={"year": 2026})
    assert dashain.status_code == 200
    start_date = dashain.json()["dates"]["start_date"]

    dispatch1 = client.post("/v2/api/webhooks/dispatch", params={"date": start_date})
    assert dispatch1.status_code == 200
    body1 = dispatch1.json()
    assert body1["sent"] >= 1

    dispatch2 = client.post("/v2/api/webhooks/dispatch", params={"date": start_date})
    assert dispatch2.status_code == 200
    body2 = dispatch2.json()
    assert body2["skipped_duplicate"] >= 1

    fetched = client.get(f"/v2/api/webhooks/{sub_id}")
    assert fetched.status_code == 200

    deleted = client.delete(f"/v2/api/webhooks/{sub_id}")
    assert deleted.status_code == 200


def test_webhook_rejects_invalid_url():
    resp = client.post(
        "/v2/api/webhooks/subscribe",
        json={
            "subscriber_url": "ftp://invalid",
            "festivals": ["dashain"],
            "remind_days_before": [1],
        },
    )
    assert resp.status_code == 400
