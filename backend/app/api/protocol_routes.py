"""Parva Protocol public preview API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.protocol_service import (
    ProtocolError,
    compatibility_levels_payload,
    issue_calendar_credential_payload,
    offline_bundle_manifest_payload,
    protocol_capabilities_payload,
    protocol_version_payload,
    run_conformance_payload,
    schema_index_payload,
    spec_index_payload,
    verify_calendar_credential_payload,
)

router = APIRouter(prefix="/api/protocol", tags=["protocol"])


class ConformanceRequest(BaseModel):
    target: str = "local"
    level: str = "parva_core"


class CredentialIssueRequest(BaseModel):
    claim_type: str = "date_conversion"
    bs_date: str = Field(..., examples=["2083-01-01"])
    release_id: str | None = None
    evidence_packet_id: str | None = None


class CredentialVerifyRequest(BaseModel):
    credential: dict[str, Any]


def _raise_protocol_error(exc: ProtocolError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={"code": exc.code, "message": str(exc)},
    ) from exc


@router.get("/version")
async def get_protocol_version() -> dict[str, Any]:
    return protocol_version_payload()


@router.get("/capabilities")
async def get_protocol_capabilities() -> dict[str, Any]:
    return protocol_capabilities_payload()


@router.get("/specs")
async def list_protocol_specs() -> dict[str, Any]:
    return spec_index_payload()


@router.get("/schemas")
async def list_protocol_schemas() -> dict[str, Any]:
    return schema_index_payload()


@router.get("/compatibility-levels")
async def list_compatibility_levels() -> dict[str, Any]:
    return compatibility_levels_payload()


@router.post("/conformance/run")
async def run_conformance(payload: ConformanceRequest) -> dict[str, Any]:
    try:
        return run_conformance_payload(target=payload.target, level=payload.level)
    except ProtocolError as exc:
        _raise_protocol_error(exc)


@router.post("/credentials/issue")
async def issue_credential(payload: CredentialIssueRequest) -> dict[str, Any]:
    try:
        return issue_calendar_credential_payload(payload.model_dump())
    except ProtocolError as exc:
        _raise_protocol_error(exc)


@router.post("/credentials/verify")
async def verify_credential(payload: CredentialVerifyRequest) -> dict[str, Any]:
    try:
        return verify_calendar_credential_payload(payload.credential)
    except ProtocolError as exc:
        _raise_protocol_error(exc)


@router.get("/credentials/schema")
async def get_credential_schema() -> dict[str, Any]:
    return {
        "schema_id": "calendar-credential",
        "path": "schemas/parva-protocol/calendar-credential.schema.json",
    }


@router.get("/offline-bundle/manifest")
async def get_offline_bundle_manifest() -> dict[str, Any]:
    return offline_bundle_manifest_payload()
