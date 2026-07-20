"""Temporal trust infrastructure contract checks."""

from __future__ import annotations

from app.main import app
from app.services.trust_infrastructure_service import (
    DEFAULT_RELEASE_ID,
    build_compliance_decision_evidence_packet,
    build_date_conversion_evidence_packet,
    diff_releases_payload,
    validate_public_trust_artifacts,
)
from fastapi.testclient import TestClient

client = TestClient(app)


def test_trust_capabilities_explain_public_boundaries() -> None:
    response = client.get("/v3/api/trust/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "temporal_trust_infrastructure"
    assert body["active_release_id"] == DEFAULT_RELEASE_ID
    assert "date_conversion_evidence_packet" in body["public_surfaces"]
    assert "official_calendar_publication" in body["not_claimed"]


def test_source_registry_and_source_detail_are_public_safe() -> None:
    response = client.get("/v3/api/trust/sources")

    assert response.status_code == 200
    body = response.json()
    assert body["release_id"] == DEFAULT_RELEASE_ID
    tiers = {source["tier"] for source in body["sources"]}
    assert "official_verified" not in tiers
    assert "official" in tiers
    assert "software_table_reference" in tiers
    assert "publisher_reference" in tiers
    assert "research_private" not in tiers

    source_id = body["sources"][0]["id"]
    detail = client.get(f"/v3/api/trust/sources/{source_id}")
    assert detail.status_code == 200
    assert detail.json()["source"]["id"] == source_id


def test_release_manifest_and_unknown_release_behavior() -> None:
    response = client.get("/v3/api/trust/releases")
    assert response.status_code == 200
    body = response.json()
    assert body["active_release_id"] == DEFAULT_RELEASE_ID
    assert body["releases"][0]["release_id"] == DEFAULT_RELEASE_ID
    assert body["releases"][0]["manifest_hash"].startswith("sha256:")

    detail = client.get(f"/v3/api/trust/releases/{DEFAULT_RELEASE_ID}")
    assert detail.status_code == 200
    assert detail.json()["release"]["release_id"] == DEFAULT_RELEASE_ID

    missing = client.get("/v3/api/trust/releases/does-not-exist")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "NOT_FOUND"


def test_release_diff_and_trust_log_are_loadable() -> None:
    diff = client.get(f"/v3/api/trust/releases/{DEFAULT_RELEASE_ID}/diff/{DEFAULT_RELEASE_ID}")
    assert diff.status_code == 200
    body = diff.json()
    assert body["summary"]["sources_added"] == 0
    assert body["summary"]["sources_changed"] == 0
    assert body["diff_scope"] == "manifest_source_artifact_only"

    log = client.get("/v3/api/trust/log")
    assert log.status_code == 200
    assert log.json()["entries"]
    assert log.json()["entries"][0]["entry_hash"].startswith("sha256:")


def test_date_conversion_evidence_packet_contains_release_source_and_hash() -> None:
    response = client.post(
        "/v3/api/trust/evidence/date-conversion",
        json={"ad_date": "2026-04-14"},
    )

    assert response.status_code == 200
    packet = response.json()
    assert packet["packet_type"] == "date_conversion"
    assert packet["release"]["release_id"] == DEFAULT_RELEASE_ID
    assert packet["sources"]
    assert packet["confidence"] == "official_verified"
    assert packet["integrity"]["packet_hash"].startswith("sha256:")
    assert packet["integrity"]["signature_status"] == "unsigned_public_preview"
    assert packet["trace_id"] == response.headers["X-Request-ID"]


def test_compliance_evidence_packet_preserves_review_metadata() -> None:
    response = client.post(
        "/v3/api/trust/evidence/compliance-decision",
        json={"profile_id": "nepal_banking_general", "bs_date": "2085-04-02"},
    )

    assert response.status_code == 200
    packet = response.json()
    assert packet["packet_type"] == "compliance_decision"
    assert packet["result"]["decision"]["requires_human_review"] is True
    assert packet["confidence"] == "unsupported"
    assert packet["claim_boundary"] == "enterprise_decision_support_not_legal_authority"


def test_evidence_packet_hash_is_stable_with_fixed_inputs() -> None:
    first = build_date_conversion_evidence_packet(
        ad_date="2026-04-14",
        trace_id="fixed-trace",
        generated_at="2026-05-13T00:00:00Z",
    )
    second = build_date_conversion_evidence_packet(
        ad_date="2026-04-14",
        trace_id="fixed-trace",
        generated_at="2026-05-13T00:00:00Z",
    )
    assert first["packet_id"] == second["packet_id"]
    assert first["integrity"]["packet_hash"] == second["integrity"]["packet_hash"]


def test_release_pinning_header_and_query_are_validated() -> None:
    ok = client.get("/v3/api/trust/sources", headers={"x-parva-release-id": DEFAULT_RELEASE_ID})
    assert ok.status_code == 200

    missing = client.post(
        "/v3/api/trust/evidence/date-conversion?release_id=missing-release",
        json={"ad_date": "2026-04-14"},
    )
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "NOT_FOUND"


def test_public_demo_profile_keeps_safe_trust_endpoints(monkeypatch) -> None:
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    monkeypatch.setenv("PARVA_ENV", "public")
    monkeypatch.setenv("PARVA_SOURCE_URL", "https://github.com/dantwoashim/Project_Parva")
    monkeypatch.setenv("PARVA_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("PARVA_PROVENANCE_ATTESTATION_KEY", "test-provenance-key")

    from app.bootstrap.app_factory import create_app

    public_demo_client = TestClient(create_app())
    assert public_demo_client.get("/v3/api/trust/capabilities").status_code == 200
    paths = public_demo_client.get("/openapi.json").json()["paths"]
    assert "/v3/api/trust/capabilities" in paths
    assert "/v3/api/compliance/profiles" not in paths


def test_trust_service_verifies_public_artifacts() -> None:
    result = validate_public_trust_artifacts()
    assert result["ok"] is True
    assert result["active_release_id"] == DEFAULT_RELEASE_ID
    assert result["source_count"] >= 1
    assert result["trust_log_entries"] >= 1


def test_release_diff_service_same_release_has_no_changes() -> None:
    payload = diff_releases_payload(DEFAULT_RELEASE_ID, DEFAULT_RELEASE_ID)
    assert payload["summary"]["sources_added"] == 0
    assert payload["summary"]["artifacts_changed"] == 0


def test_compliance_packet_service_works_without_api() -> None:
    packet = build_compliance_decision_evidence_packet(
        profile_id="nepal_private_company_default",
        bs_date="2082-04-02",
        trace_id="fixed-trace",
        generated_at="2026-05-13T00:00:00Z",
    )
    assert packet["packet_type"] == "compliance_decision"
    assert packet["result"]["decision"]["requires_human_review"] is False
