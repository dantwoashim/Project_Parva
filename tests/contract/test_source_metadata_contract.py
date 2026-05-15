"""Source-aware temporal contract checks."""

from __future__ import annotations

import json
from pathlib import Path

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _meta(body: dict) -> dict:
    meta = body.get("meta")
    assert isinstance(meta, dict)
    assert isinstance(meta.get("source"), dict)
    assert isinstance(meta["source"].get("id"), str)
    assert isinstance(meta["source"].get("label"), str)
    assert isinstance(meta["source"].get("tier"), str)
    assert isinstance(meta["source"].get("authority"), str)
    assert isinstance(meta.get("confidence"), str)
    assert isinstance(meta.get("data_version"), str)
    assert isinstance(meta.get("claim_boundary"), str)
    assert isinstance(meta.get("warnings"), list)
    assert isinstance(meta.get("trace_id"), str)
    return meta


def test_core_public_calendar_endpoints_include_source_metadata() -> None:
    convert = client.get("/v3/api/calendar/convert", params={"date": "2026-04-14"})
    assert convert.status_code == 200
    convert_meta = _meta(convert.json())
    assert convert_meta["trace_id"] == convert.headers["X-Request-ID"]
    assert convert_meta["confidence"] == "official_verified"
    assert convert_meta["source"]["tier"] == "official"
    assert convert_meta["claim_boundary"] == "official_source_interpretation_not_legal_advice"

    bs_to_ad = client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2083, "month": 1, "day": 1},
    )
    assert bs_to_ad.status_code == 200
    bs_to_ad_meta = _meta(bs_to_ad.json())
    assert bs_to_ad_meta["trace_id"] == bs_to_ad.headers["X-Request-ID"]
    assert bs_to_ad_meta["confidence"] == "official_verified"

    today = client.get("/v3/api/calendar/today")
    assert today.status_code == 200
    today_meta = _meta(today.json())
    assert today_meta["trace_id"] == today.headers["X-Request-ID"]
    assert "not_legal_tax_or_banking_contract_authority" in today_meta["warnings"]


def test_unstructured_static_lookup_rows_are_not_marked_official() -> None:
    response = client.post(
        "/v3/api/calendar/bs-to-gregorian",
        json={"year": 2075, "month": 1, "day": 1},
    )

    assert response.status_code == 200
    meta = _meta(response.json())
    assert meta["confidence"] == "source_backed"
    assert meta["source"]["tier"] == "software_table_reference"
    assert meta["source"]["id"] == "parva_static_lookup_table"
    assert "official" not in {meta["confidence"], meta["source"]["tier"]}
    assert "static_lookup_without_structured_official_provenance" in meta["warnings"]


def test_future_bs_capabilities_are_labeled_research_preview() -> None:
    response = client.get("/v4/api/future-bs/capabilities")

    assert response.status_code == 200
    body = response.json()
    meta = _meta(body)
    assert body["publication_status"] == "computed_prediction_not_official"
    assert body["maturity"] == "research_preview"
    assert body["claim_boundary"] == meta["claim_boundary"]
    assert meta["confidence"] == "research_preview"
    assert meta["maturity"] == "research_preview"
    assert meta["source"]["tier"] == "research_private"
    assert meta["claim_boundary"] == "research_preview_not_safe_for_legal_or_payroll_use"
    assert "computed_prediction_not_official" in meta["warnings"]


def test_enterprise_temporal_responses_include_source_metadata() -> None:
    response = client.get("/v3/api/enterprise/fiscal-year/2082")

    assert response.status_code == 200
    meta = _meta(response.json())
    assert meta["trace_id"] == response.headers["X-Request-ID"]
    assert meta["confidence"] == "official_verified"
    assert meta["source"]["id"] == "parva_structured_official_bs_window"


def test_envelope_opt_in_preserves_source_metadata() -> None:
    response = client.get(
        "/v3/api/calendar/today",
        headers={"X-Parva-Envelope": "data-meta"},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"data", "meta"}
    envelope_meta = body["meta"]
    source = envelope_meta.get("source")
    assert isinstance(source, dict)
    assert source["id"] == body["data"]["meta"]["source"]["id"]
    assert envelope_meta["data_version"] == body["data"]["meta"]["data_version"]
    assert envelope_meta["claim_boundary"] == body["data"]["meta"]["claim_boundary"]
    assert envelope_meta["warnings"] == body["data"]["meta"]["warnings"]
    assert envelope_meta["trace_id"] == response.headers["X-Request-ID"]


def test_unsupported_calendar_range_returns_clear_error() -> None:
    response = client.get("/v3/api/calendar/dual-month", params={"year": 1800, "month": 1})

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "BAD_REQUEST"
    assert body["error"]["trace_id"] == body["request_id"]
    assert "Year must be between" in body["error"]["message"]


def test_static_openapi_docs_include_source_aware_metadata_schema() -> None:
    schema_path = Path("docs/api-docs/openapi.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    schemas = schema["components"]["schemas"]
    assert "SourceAwareMeta" in schemas
    source_meta = schemas["SourceAwareMeta"]
    assert "source" in source_meta["properties"]
    assert "confidence" in source_meta["properties"]
    assert "data_version" in source_meta["properties"]
    assert "claim_boundary" in source_meta["properties"]
    assert "warnings" in source_meta["properties"]
    assert "trace_id" in source_meta["properties"]
