"""Source-record ingestion for public-safe evidence."""

from __future__ import annotations

from typing import Any

from .models import SourceRecord


def ingest_source_record(payload: dict[str, Any]) -> SourceRecord:
    record_kwargs = {
        "source_id": str(payload["source_id"]),
        "source_type": str(payload["source_type"]),
        "source_reference": str(payload.get("source_url") or payload.get("source_reference") or ""),
        "source_tier": str(payload["source_tier"]),
        "public_safe": bool(payload.get("public_safe", True)),
        "authority_boundary": str(payload.get("authority_boundary") or "source_backed_not_authority"),
    }
    if payload.get("ingestion_time"):
        record_kwargs["ingestion_time"] = str(payload["ingestion_time"])
    record = SourceRecord(**record_kwargs)
    issues = record.validate()
    if issues:
        raise ValueError("; ".join(issues))
    return record
