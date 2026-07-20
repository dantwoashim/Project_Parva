"""TimeGraph contract checks."""

from __future__ import annotations

import json
from pathlib import Path

from app.bootstrap.app_factory import create_app
from app.main import app
from app.services.timegraph_service import (
    bs_ad_fact_id,
    build_public_timegraph,
    trace_fact_payload,
    validate_public_timegraph,
)
from fastapi.testclient import TestClient

client = TestClient(app)


def test_timegraph_capabilities_are_public_safe() -> None:
    response = client.get("/v3/api/timegraph/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["surface"] == "parva_timegraph"
    assert body["status"] == "public_preview"
    assert body["max_limit"] == 200
    assert "official_calendar_publication" not in json.dumps(body)
    assert "bs_ad_mapping" in body["fact_types"]
    assert "SUPPORTED_BY" in body["relationship_types"]


def test_public_timegraph_builds_from_release_source_and_mapping_facts() -> None:
    graph = build_public_timegraph()
    sample_fact_id = bs_ad_fact_id(2083, 1, 1)

    assert validate_public_timegraph()["ok"] is True
    assert sample_fact_id in graph.facts
    assert "parva_structured_official_bs_window" in graph.facts[sample_fact_id].source_ids
    assert graph.facts[sample_fact_id].object["date"] == "2026-04-14"
    assert "fact_source_claim_parva_public_bs_ad_corpus" in graph.facts
    assert "fact_release_membership_parva_bs_public_demo_parva_public_bs_ad_corpus" in graph.facts


def test_fact_listing_is_bounded_and_queryable() -> None:
    response = client.get("/v3/api/timegraph/facts", params={"fact_type": "bs_ad_mapping", "limit": 5})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 5
    assert body["pagination"]["limit"] == 5
    assert body["pagination"]["has_more"] is True
    assert body["meta"]["claim_boundary"] == "timegraph_query_not_legal_authority"

    too_large = client.get("/v3/api/timegraph/facts", params={"limit": 1000})
    assert too_large.status_code == 422


def test_fact_detail_trace_and_relationships_are_linked() -> None:
    fact_id = bs_ad_fact_id(2083, 1, 1)
    detail = client.get(f"/v3/api/timegraph/facts/{fact_id}")
    trace = client.get(f"/v3/api/timegraph/facts/{fact_id}/trace")
    relationships = client.get(f"/v3/api/timegraph/entities/{fact_id}/relationships")

    assert detail.status_code == 200
    assert detail.json()["fact"]["fact_id"] == fact_id
    assert any(rel["type"] == "SUPPORTED_BY" for rel in detail.json()["relationships"])
    assert trace.status_code == 200
    assert trace.json()["trace"]["sources"]
    assert trace.json()["trace"]["release"]["release_id"] == "parva-bs-public-demo"
    assert trace.json()["trace"]["evidence_packets"][0]["packet_type"] == "date_conversion"
    assert relationships.status_code == 200
    assert relationships.json()["relationships"]


def test_date_source_release_profile_and_post_queries_work() -> None:
    date_response = client.get("/v3/api/timegraph/date/BS/2083-01-01")
    source_response = client.get("/v3/api/timegraph/sources/parva_structured_official_bs_window/facts")
    release_response = client.get("/v3/api/timegraph/releases/parva-bs-public-demo/facts")
    profile_response = client.get("/v3/api/timegraph/profiles/nepal_private_company_default/facts")
    post_query = client.post(
        "/v3/api/timegraph/query",
        json={"fact_type": "weekday", "date": "2026-04-14", "calendar": "AD", "limit": 10},
    )

    assert date_response.status_code == 200
    assert any(item["fact_type"] == "bs_ad_mapping" for item in date_response.json()["items"])
    assert source_response.status_code == 200
    assert source_response.json()["items"]
    assert release_response.status_code == 200
    assert release_response.json()["items"]
    assert profile_response.status_code == 200
    assert any(item["fact_type"] == "profile_policy" for item in profile_response.json()["items"])
    assert post_query.status_code == 200
    assert post_query.json()["items"][0]["object"]["weekday"] == "TUESDAY"


def test_conflict_model_is_fixture_labeled_not_real_calendar_claim() -> None:
    response = client.get("/v3/api/timegraph/conflicts")

    assert response.status_code == 200
    body = response.json()
    assert body["conflicts"]
    conflict = body["conflicts"][0]
    assert conflict["status"] == "fixture_only"
    assert conflict["metadata"]["fixture_only"] is True
    assert "fixture_conflict_not_real_calendar_claim" in conflict["warnings"]


def test_evidence_and_compliance_payloads_reference_timegraph_fact_ids() -> None:
    evidence = client.post(
        "/v3/api/trust/evidence/date-conversion",
        json={"ad_date": "2026-04-14"},
    )
    compliance = client.post(
        "/v3/api/compliance/evaluate-date",
        json={"profile_id": "nepal_private_company_default", "bs_date": "2082-04-02"},
    )

    assert evidence.status_code == 200
    assert bs_ad_fact_id(2083, 1, 1) in evidence.json()["fact_ids"]
    assert compliance.status_code == 200
    body = compliance.json()
    assert "fact_working_day_nepal_private_company_default_2082_04_02" in body["fact_ids"]
    assert body["trace_url"].endswith("/trace")


def test_unknown_fact_source_and_release_fail_clearly() -> None:
    missing_fact = client.get("/v3/api/timegraph/facts/missing-fact")
    missing_source = client.get("/v3/api/timegraph/sources/missing-source/facts")
    missing_release = client.get("/v3/api/timegraph/releases/missing-release/facts")

    assert missing_fact.status_code == 404
    assert "unknown fact id" in missing_fact.json()["detail"]
    assert missing_source.status_code == 404
    assert "unknown source id" in missing_source.json()["detail"]
    assert missing_release.status_code in {400, 404}


def test_public_graph_does_not_expose_private_or_local_paths() -> None:
    trace = trace_fact_payload(bs_ad_fact_id(2083, 1, 1))
    serialized = json.dumps(trace)
    local_drive_markers = [f"{drive}:" + "\\" for drive in ("C", "D")]

    assert "source_archive" not in serialized
    assert all(marker not in serialized for marker in local_drive_markers)


def test_public_demo_profile_includes_safe_timegraph_routes(monkeypatch) -> None:
    monkeypatch.setenv("PARVA_ROUTE_PROFILE", "public_demo")
    monkeypatch.setenv("PARVA_ENABLE_EXPERIMENTAL_API", "false")
    monkeypatch.setenv("PARVA_SHOW_PRIVATE_SCHEMA", "false")
    public_demo_client = TestClient(create_app())

    assert public_demo_client.get("/v3/api/timegraph/capabilities").status_code == 200
    assert public_demo_client.get("/v3/api/compliance/profiles").status_code == 404
    paths = public_demo_client.get("/openapi.json").json()["paths"]
    assert "/v3/api/timegraph/capabilities" in paths
    assert "/v3/api/compliance/profiles" not in paths


def test_static_openapi_docs_exclude_timegraph_preview_surface() -> None:
    schema = json.loads(Path("docs/api-docs/openapi.json").read_text(encoding="utf-8"))
    schemas = schema["components"]["schemas"]

    assert "TemporalFact" not in schemas
    assert "TimeGraphRelationship" not in schemas
    assert "TimeGraphConflict" not in schemas
    assert "TimeGraphQuery" not in schemas
    assert "/v3/api/timegraph/facts" not in schema["paths"]
