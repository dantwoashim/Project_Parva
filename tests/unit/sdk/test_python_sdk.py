from __future__ import annotations

import importlib
import warnings

from app.main import app
from fastapi.testclient import TestClient

from sdk.python.parva_sdk import ParvaClient


def _testclient_request_fn(client: TestClient):
    def _request(method: str, path: str, params=None, json=None, timeout=None):
        del timeout
        resp = client.request(method, f"/v3/api{path}", params=params, json=json)
        assert resp.status_code == 200
        return resp.json()

    return _request


def _sdk_test_client() -> TestClient:
    return TestClient(app, client=("sdk-python-tests", 50000))


def test_python_sdk_today_and_convert_match_api():
    test_client = _sdk_test_client()
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    sdk_today = sdk.today()
    api_today = test_client.get("/v3/api/calendar/today").json()
    assert sdk_today.data["gregorian"] == api_today["gregorian"]
    assert sdk_today.meta.method == "unknown"

    sdk_convert = sdk.convert("2026-02-15")
    api_convert = test_client.get("/v3/api/calendar/convert", params={"date": "2026-02-15"}).json()
    assert sdk_convert.data["bikram_sambat"] == api_convert["bikram_sambat"]


def test_python_sdk_post_payload_serializes_numeric_coordinates():
    captured = {}

    def _request(method: str, path: str, params=None, json=None, timeout=None):
        captured["method"] = method
        captured["path"] = path
        captured["params"] = params
        captured["json"] = json
        captured["timeout"] = timeout
        return {
            "status": "ok",
            "method": "sdk_capture",
            "quality_band": "validated",
            "calculation_trace_id": "trace-capture",
        }

    sdk = ParvaClient(base_url="http://ignored", request_fn=_request)

    payload = sdk.personal_panchanga("2026-02-15", latitude=27.7172, longitude=85.3240)

    assert captured == {
        "method": "POST",
        "path": "/personal/panchanga",
        "params": None,
        "json": {
            "date": "2026-02-15",
            "lat": "27.7172",
            "lon": "85.324",
            "tz": "Asia/Kathmandu",
        },
        "timeout": 15,
    }
    assert payload.meta.method == "sdk_capture"
    assert payload.meta.trace_id == "trace-capture"
    assert payload.meta.quality_band == "validated"


def test_python_sdk_upcoming_and_observances():
    test_client = _sdk_test_client()
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    upcoming = sdk.upcoming(7)
    assert "festivals" in upcoming.data

    obs = sdk.observances("2026-10-21", preferences="nepali_hindu")
    assert "observances" in obs.data


def test_python_sdk_explain_helpers():
    test_client = _sdk_test_client()
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    explain = sdk.explain_festival("dashain", 2026)
    assert "calculation_trace_id" in explain.data

    trace = sdk.explain_trace(explain.data["calculation_trace_id"])
    assert trace.data["trace_id"] == explain.data["calculation_trace_id"]


def test_python_sdk_personal_stack_post_helpers_match_api():
    test_client = _sdk_test_client()
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    compass = sdk.temporal_compass("2026-10-21", latitude=27.7172, longitude=85.3240)
    api_compass = test_client.post(
        "/v3/api/temporal/compass",
        json={
            "date": "2026-10-21",
            "lat": "27.7172",
            "lon": "85.324",
            "tz": "Asia/Kathmandu",
            "quality_band": "computed",
        },
    ).json()
    assert compass.data["primary_readout"]["tithi_name"] == api_compass["primary_readout"]["tithi_name"]
    assert compass.meta.method == api_compass["method"]

    panchanga = sdk.personal_panchanga("2026-10-21", latitude=27.7172, longitude=85.3240)
    api_panchanga = test_client.post(
        "/v3/api/personal/panchanga",
        json={
            "date": "2026-10-21",
            "lat": "27.7172",
            "lon": "85.324",
            "tz": "Asia/Kathmandu",
        },
    ).json()
    assert panchanga.data["tithi"]["name"] == api_panchanga["tithi"]["name"]
    assert panchanga.meta.method_profile == api_panchanga["method_profile"]

    heatmap = sdk.muhurta_heatmap(
        "2026-10-21",
        ceremony_type="travel",
        latitude=27.7172,
        longitude=85.3240,
    )
    api_heatmap = test_client.post(
        "/v3/api/muhurta/heatmap",
        json={
            "date": "2026-10-21",
            "type": "travel",
            "lat": "27.7172",
            "lon": "85.324",
            "tz": "Asia/Kathmandu",
            "assumption_set": "np-mainstream-v2",
        },
    ).json()
    assert heatmap.data["best_window"]["name"] == api_heatmap["best_window"]["name"]
    assert heatmap.meta.assumption_set_id == api_heatmap["assumption_set_id"]

    muhurta_day = sdk.muhurta_day("2026-10-21", latitude=27.7172, longitude=85.3240)
    assert len(muhurta_day.data["muhurtas"]) == 30

    auspicious = sdk.auspicious_muhurta(
        "2026-10-21",
        ceremony_type="travel",
        latitude=27.7172,
        longitude=85.3240,
    )
    assert auspicious.data["type"] == "travel"
    assert "reason_codes" in auspicious.data

    rahu = sdk.rahu_kalam("2026-10-21", latitude=27.7172, longitude=85.3240)
    assert rahu.data["weekday"]


def test_python_sdk_kundali_helpers_match_api():
    test_client = _sdk_test_client()
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn(test_client))

    kundali = sdk.kundali(
        "2026-02-15T06:30:00+05:45",
        latitude=27.7172,
        longitude=85.3240,
    )
    api_kundali = test_client.post(
        "/v3/api/kundali",
        json={
            "datetime": "2026-02-15T06:30:00+05:45",
            "lat": "27.7172",
            "lon": "85.324",
            "tz": "Asia/Kathmandu",
        },
    ).json()
    assert kundali.data["lagna"]["rashi_english"] == api_kundali["lagna"]["rashi_english"]
    assert kundali.meta.method_profile == api_kundali["method_profile"]

    lagna = sdk.kundali_lagna(
        "2026-02-15T06:30:00+05:45",
        latitude=27.7172,
        longitude=85.3240,
    )
    assert lagna.data["lagna"]["rashi_english"] == kundali.data["lagna"]["rashi_english"]

    graph = sdk.kundali_graph(
        "2026-02-15T06:30:00+05:45",
        latitude=27.7172,
        longitude=85.3240,
    )
    assert graph.data["layout"]["house_nodes"]


def test_legacy_python_sdk_import_path_warns_and_reexports():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        legacy_module = importlib.reload(importlib.import_module("sdk.python.parva"))

    assert legacy_module.ParvaClient is not None
    assert legacy_module.ParvaError is not None
    assert any("deprecated" in str(item.message).lower() for item in caught)
