"""v3 routing and contract sanity checks."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_v3_openapi_and_docs_endpoints_exist():
    openapi_resp = client.get("/v3/openapi.json")
    assert openapi_resp.status_code == 200
    body = openapi_resp.json()
    assert "paths" in body

    docs_resp = client.get("/v3/docs", follow_redirects=False)
    assert docs_resp.status_code in {302, 307}


def test_v3_api_alias_works_for_core_endpoints():
    alias_today = client.get("/api/calendar/today")
    v3_today = client.get("/v3/api/calendar/today")

    assert alias_today.status_code == 200
    assert v3_today.status_code == 200
    assert v3_today.headers.get("X-Parva-Engine") == "v3"
    assert alias_today.json()["gregorian"] == v3_today.json()["gregorian"]

    v3_explain = client.get("/v3/api/festivals/dashain/explain", params={"year": 2026})
    assert v3_explain.status_code == 200
    assert "calculation_trace_id" in v3_explain.json()
