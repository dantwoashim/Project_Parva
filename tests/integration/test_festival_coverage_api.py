"""Integration tests for festival coverage and new filters."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.festivals import router


app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_festival_coverage_endpoint_returns_summary():
    res = client.get("/api/festivals/coverage")
    assert res.status_code == 200
    payload = res.json()

    assert payload["target_rules"] == 300
    assert payload["total_rules"] >= 300
    assert "by_type" in payload
    assert "by_status" in payload
    assert "by_rule_family" in payload
    assert "variant_profile_coverage_pct" in payload
    assert "festival_content_count" in payload
    assert payload["by_source"].get("rule_ingestion_seed_v1", 0) > 0


def test_festival_source_filter_works():
    res = client.get("/api/festivals?source=festival_rules_v3")
    assert res.status_code == 200
    payload = res.json()

    assert payload["total"] > 0
    ids = {festival["id"] for festival in payload["festivals"]}
    assert "dashain" in ids


def test_tradition_filter_returns_newari_subset():
    res = client.get("/api/festivals?tradition=newari")
    assert res.status_code == 200
    payload = res.json()
    assert payload["total"] > 0

    for festival in payload["festivals"]:
        assert "newari" in festival["category"].lower()
