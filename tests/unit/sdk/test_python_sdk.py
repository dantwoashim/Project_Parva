from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from sdk.python.parva_sdk import ParvaClient


def _testclient_request_fn(client: TestClient):
    def _request(method: str, path: str, params=None):
        assert method == "GET"
        resp = client.get(f"/v3/api{path}", params=params)
        assert resp.status_code == 200
        return resp.json()

    return _request


def test_python_sdk_today_and_convert_match_api():
    test_client = TestClient(app)
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    sdk_today = sdk.today()
    api_today = test_client.get("/v3/api/calendar/today").json()
    assert sdk_today.data["gregorian"] == api_today["gregorian"]
    assert sdk_today.meta.method == "unknown"

    sdk_convert = sdk.convert("2026-02-15")
    api_convert = test_client.get("/v3/api/calendar/convert", params={"date": "2026-02-15"}).json()
    assert sdk_convert.data["bikram_sambat"] == api_convert["bikram_sambat"]


def test_python_sdk_upcoming_and_observances():
    test_client = TestClient(app)
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    upcoming = sdk.upcoming(7)
    assert "festivals" in upcoming.data

    obs = sdk.observances("2026-10-21", preferences="nepali_hindu")
    assert "observances" in obs.data


def test_python_sdk_explain_helpers():
    test_client = TestClient(app)
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    explain = sdk.explain_festival("dashain", 2026)
    assert "calculation_trace_id" in explain.data

    trace = sdk.explain_trace(explain.data["calculation_trace_id"])
    assert trace.data["trace_id"] == explain.data["calculation_trace_id"]
