from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from sdk.python.parva_sdk import ParvaClient


def _testclient_request_fn_v5(client: TestClient):
    def _request(method: str, path: str, params=None):
        assert method == "GET"
        resp = client.get(f"/v5/api{path}", params=params)
        assert resp.status_code == 200
        return resp.json()

    return _request


def test_python_sdk_v5_envelope_meta_is_parsed():
    test_client = TestClient(app)
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn_v5(test_client))

    today = sdk.today()
    assert today.data["gregorian"]
    assert today.meta.confidence.level in {"official", "computed", "estimated", "unknown"}
    assert today.meta.provenance.dataset_hash
    assert today.meta.provenance.rules_hash
    assert today.meta.provenance.snapshot_id
    assert today.meta.provenance.signature


def test_python_sdk_v5_resolve_and_trace_verify():
    test_client = TestClient(app)
    sdk = ParvaClient(base_url="http://ignored", request_fn=_testclient_request_fn_v5(test_client))

    resolved = sdk.resolve("2026-10-21")
    assert resolved.data["bikram_sambat"]["year"] == 2083
    trace_id = resolved.meta.trace_id
    assert trace_id

    verification = sdk.verify_trace(trace_id)
    assert verification.data["trace_id"] == trace_id
    assert verification.data["checks"]["exists"] is True
    assert verification.data["valid"] is True
