"""Integration tests for late-phase festival truth/dispute surfaces."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_dispute_atlas_returns_truth_ladder_and_live_rows():
    response = client.get("/api/festivals/disputes", params={"year": 2026, "limit": 12})
    assert response.status_code == 200

    body = response.json()
    assert body["year"] == 2026
    assert isinstance(body["truth_ladder"], list)
    assert len(body["truth_ladder"]) >= 5
    assert isinstance(body["disputes"], list)
    assert body["total_items"] == len(body["disputes"])
    assert any(item["boundary_radar"] in {"one_day_sensitive", "high_disagreement_risk"} for item in body["disputes"])


def test_dispute_atlas_includes_known_authority_conflict():
    response = client.get("/api/festivals/disputes", params={"year": 2026, "limit": 30})
    assert response.status_code == 200

    body = response.json()
    ghode_jatra = next(item for item in body["disputes"] if item["festival_id"] == "ghode-jatra")
    assert ghode_jatra["authority_conflict"] is True
    assert ghode_jatra["boundary_radar"] == "high_disagreement_risk"
    assert ghode_jatra["stability_score"] < 0.8
    assert len(ghode_jatra["alternate_candidates"]) >= 1


def test_proof_capsule_returns_portable_selection_and_risk_sections():
    response = client.get(
        "/api/festivals/ghode-jatra/proof-capsule",
        params={"year": 2026, "authority_mode": "authority_compare", "risk_mode": "strict"},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["festival_id"] == "ghode-jatra"
    assert body["year"] == 2026
    assert body["request"]["authority_mode"] == "authority_compare"
    assert body["selection"]["engine_path"]
    assert body["selection"]["support_tier"] in {"authoritative", "computed", "conflicted", "heuristic", "estimated"}
    assert body["source_lineage"]["authority_conflict"] is True
    assert body["risk"]["boundary_radar"] == "high_disagreement_risk"
    assert body["risk"]["risk_mode"] == "strict"
    assert isinstance(body["risk"]["truth_ladder"], list)
    assert body["calculation_trace_id"]


def test_festival_detail_and_explain_surface_risk_fields():
    detail_response = client.get(
        "/api/festivals/ghode-jatra",
        params={"year": 2026, "authority_mode": "authority_compare", "risk_mode": "strict"},
    )
    explain_response = client.get(
        "/api/festivals/ghode-jatra/explain",
        params={"year": 2026, "authority_mode": "authority_compare", "risk_mode": "strict"},
    )

    assert detail_response.status_code == 200
    assert explain_response.status_code == 200

    detail = detail_response.json()
    explain = explain_response.json()

    assert detail["dates"]["boundary_radar"] == "high_disagreement_risk"
    assert isinstance(detail["dates"]["stability_score"], float)
    assert detail["dates"]["risk_mode"] == "strict"
    assert detail["dates"]["abstained"] is True
    assert detail["dates"]["recommended_action"]

    assert explain["boundary_radar"] == "high_disagreement_risk"
    assert isinstance(explain["stability_score"], float)
    assert explain["risk_mode"] == "strict"
    assert explain["abstained"] is True
    assert explain["recommended_action"]
