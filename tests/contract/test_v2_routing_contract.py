"""Week 33-34 contract checks for v2 paths and deprecation headers."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_v2_openapi_and_docs_endpoints_exist():
    openapi_resp = client.get("/v2/openapi.json")
    assert openapi_resp.status_code == 200
    body = openapi_resp.json()
    assert "paths" in body

    docs_resp = client.get("/v2/docs", follow_redirects=False)
    assert docs_resp.status_code in {302, 307}


def test_versioned_api_alias_works():
    old_resp = client.get("/api/calendar/today")
    new_resp = client.get("/v2/api/calendar/today")

    assert old_resp.status_code == 200
    assert new_resp.status_code == 200

    old_body = old_resp.json()
    new_body = new_resp.json()

    assert old_body["engine_version"] == "v2"
    assert new_body["engine_version"] == "v2"
    assert old_body["gregorian"] == new_body["gregorian"]


def test_unversioned_api_has_deprecation_headers():
    resp = client.get("/api/calendar/convert", params={"date": "2026-02-15"})
    assert resp.status_code == 200
    assert resp.headers.get("Deprecation") == "true"
    assert resp.headers.get("Sunset") is not None
    assert "successor-version" in (resp.headers.get("Link") or "")


def test_v2_api_has_migration_headers():
    resp = client.get("/v2/api/calendar/convert", params={"date": "2026-02-15"})
    assert resp.status_code == 200
    assert resp.headers.get("Deprecation") == "true"
    assert resp.headers.get("Sunset") is not None
    assert "successor-version" in (resp.headers.get("Link") or "")
