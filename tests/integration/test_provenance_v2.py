from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_and_verify_snapshot_v2():
    created = client.post("/v2/api/provenance/snapshot/create")
    assert created.status_code == 200
    payload = created.json()
    assert payload.get("snapshot_id")

    verify = client.get(f"/v2/api/provenance/snapshot/{payload['snapshot_id']}/verify")
    assert verify.status_code == 200
    details = verify.json()
    assert details["snapshot_id"] == payload["snapshot_id"]
    assert "valid" in details


def test_date_response_contains_provenance_and_verify_url():
    resp = client.get("/v2/api/festivals/dashain", params={"year": 2026})
    assert resp.status_code == 200
    body = resp.json()

    provenance = body.get("provenance")
    assert provenance is not None
    assert provenance.get("dataset_hash")
    assert provenance.get("rules_hash")
    assert provenance.get("snapshot_id")
    assert provenance.get("verify_url")

    verify_url = provenance["verify_url"]
    proof = client.get(verify_url)
    assert proof.status_code == 200
    proof_body = proof.json()
    assert proof_body.get("festival_id") == "dashain"
    assert proof_body.get("verified") is True


def test_query_proof_endpoint():
    root = client.get("/v2/api/provenance/root")
    assert root.status_code == 200
    snapshot_id = root.json().get("snapshot_id")

    params = {"festival": "dashain", "year": 2026}
    if snapshot_id:
        params["snapshot"] = snapshot_id

    resp = client.get("/v2/api/provenance/proof", params=params)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["festival_id"] == "dashain"
    assert payload["verified"] is True
