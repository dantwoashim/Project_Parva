from __future__ import annotations

from app.bootstrap.app_factory import create_app
from app.services.impact_service import (
    event_schema_payload,
    semantic_release_diff_payload,
    simulate_change_set_payload,
    simulate_release_diff_payload,
)
from fastapi.testclient import TestClient


def test_semantic_self_diff_has_no_changes() -> None:
    diff = semantic_release_diff_payload("parva-bs-public-demo", "parva-bs-public-demo")
    assert diff["summary"]["facts_changed"] == 0
    assert diff["changes"] == []


def test_fixture_release_diff_detects_registered_impacts() -> None:
    run = simulate_release_diff_payload(
        "parva-bs-public-demo",
        "parva-bs-public-demo",
        include_fixture=True,
    )
    assert run["summary"]["changes_analyzed"] == 1
    assert run["summary"]["impacts_found"] >= 1
    assert any(item["severity"] in {"medium", "high"} for item in run["impacts"])


def test_stale_evidence_is_historically_valid_not_false() -> None:
    run = simulate_change_set_payload(
        {
            "change_set_id": "evidence_fact_change",
            "changes": [
                {
                    "change_type": "FACT_CHANGED",
                    "entity_type": "temporal_fact",
                    "entity_id": "fact_bs_ad_2082_01_01",
                }
            ],
        }
    )
    stale = [item for item in run["impacts"] if item["impact_type"] == "evidence_packet_stale"]
    assert stale
    assert "EVIDENCE_PACKET_HISTORICALLY_VALID" in stale[0]["reason_codes"]


def test_impact_event_schema_is_unsigned_preview() -> None:
    schema = event_schema_payload()["schema"]
    assert "unsigned_preview" in schema["properties"]["signature_status"]["enum"]


def test_impact_api_endpoints() -> None:
    app = create_app()
    client = TestClient(app)
    assert client.get("/v3/api/impact/capabilities").status_code == 200
    response = client.post(
        "/v3/api/impact/simulate-release-diff",
        json={
            "from_release_id": "parva-bs-public-demo",
            "to_release_id": "parva-bs-public-demo",
            "include_fixture": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["summary"]["impacts_found"] >= 1
