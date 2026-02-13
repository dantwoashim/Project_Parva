from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_transparency(tmp_path: Path, monkeypatch):
    from app.provenance import transparency

    monkeypatch.setattr(transparency, "TRANSPARENCY_DIR", tmp_path)
    monkeypatch.setattr(transparency, "TRANSPARENCY_LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(transparency, "ANCHOR_LOG", tmp_path / "anchors.jsonl")
    yield


def test_snapshot_create_appends_transparency_event():
    created = client.post("/v2/api/provenance/snapshot/create")
    assert created.status_code == 200

    log_resp = client.get("/v2/api/provenance/transparency/log")
    assert log_resp.status_code == 200
    body = log_resp.json()
    assert body["total_entries"] >= 1
    assert any(e["event_type"] == "snapshot_created" for e in body["entries"])

    audit = client.get("/v2/api/provenance/transparency/audit")
    assert audit.status_code == 200
    assert audit.json()["valid"] is True


def test_transparency_anchor_prepare_record_and_list():
    prepared = client.get("/v2/api/provenance/transparency/anchor/prepare", params={"note": "beta"})
    assert prepared.status_code == 200
    payload = prepared.json()
    assert "head_hash" in payload

    recorded = client.post(
        "/v2/api/provenance/transparency/anchor/record",
        params={"tx_ref": "0xdeadbeef", "network": "testnet"},
    )
    assert recorded.status_code == 200

    anchors = client.get("/v2/api/provenance/transparency/anchors")
    assert anchors.status_code == 200
    assert anchors.json()["count"] >= 1


def test_dashboard_endpoint_reads_artifact(tmp_path: Path, monkeypatch):
    from app.provenance import routes as provenance_routes

    dashboard_path = tmp_path / "dashboard.json"
    dashboard_payload = {"release_channel": "year2-global-beta", "uptime_percent": 99.0}
    dashboard_path.write_text(json.dumps(dashboard_payload), encoding="utf-8")

    monkeypatch.setattr(provenance_routes, "PUBLIC_BETA_DASHBOARD", dashboard_path)

    resp = client.get("/v2/api/provenance/dashboard")
    assert resp.status_code == 200
    assert resp.json()["release_channel"] == "year2-global-beta"
