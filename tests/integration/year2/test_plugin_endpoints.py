from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_calendars_endpoint_lists_plugins():
    resp = client.get("/v2/api/engine/calendars")
    assert resp.status_code == 200
    body = resp.json()
    ids = {c["plugin_id"] for c in body["calendars"]}
    assert {"bs", "ns", "tibetan", "islamic", "hebrew", "chinese"}.issubset(ids)


def test_engine_convert_tibetan():
    resp = client.get("/v2/api/engine/convert", params={"date": "2026-02-15", "calendar": "tibetan"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["calendar"] == "tibetan"
    assert body["result"]["year"] == 2153


def test_tibetan_observance_plugin():
    resp = client.get(
        "/v2/api/engine/observances",
        params={"plugin": "tibetan_buddhist", "rule_id": "saga-dawa", "year": 2026},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["plugin"] == "tibetan_buddhist"
    assert body["result"]["rule_id"] == "saga-dawa"


def test_islamic_observance_announced_mode():
    resp = client.get(
        "/v2/api/engine/observances",
        params={"plugin": "islamic", "rule_id": "eid-al-fitr", "year": 2026, "mode": "announced"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["plugin"] == "islamic"
    assert body["mode"] == "announced"
    assert body["result"]["method"] == "announced_override"
    assert body["result"]["start_date"] == "2026-03-20"


def test_engine_convert_hebrew_and_islamic():
    islamic = client.get("/v2/api/engine/convert", params={"date": "2026-02-15", "calendar": "islamic"})
    assert islamic.status_code == 200
    assert islamic.json()["result"]["year"] == 1447

    hebrew = client.get("/v2/api/engine/convert", params={"date": "2026-02-15", "calendar": "hebrew"})
    assert hebrew.status_code == 200
    assert hebrew.json()["result"]["year"] == 5786

    chinese = client.get("/v2/api/engine/convert", params={"date": "2026-02-20", "calendar": "chinese"})
    assert chinese.status_code == 200
    assert chinese.json()["result"]["year"] == 2026


def test_festival_variants_endpoint():
    resp = client.get("/v2/api/festivals/shivaratri/variants", params={"year": 2026})
    assert resp.status_code == 200
    body = resp.json()
    assert body["festival_id"] == "shivaratri"
    assert len(body["variants"]) >= 1
    assert "coverage" in body
    assert body["coverage"]["rule_family"] in {
        "lunar_month_tithi",
        "lunar_bs_tithi",
        "profile_variant",
        "unknown",
    }


def test_festival_variants_profile_filter():
    resp = client.get(
        "/v2/api/festivals/shivaratri/variants",
        params={"year": 2026, "profile": "diaspora-north-indian"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["profile_filter"] == "diaspora-north-indian"
    assert all(v["profile_id"] == "diaspora-north-indian" for v in body["variants"])
