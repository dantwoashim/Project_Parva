"""Helpers for v4/v5 data envelope normalization."""

from __future__ import annotations

import hashlib
from typing import Any

from app.provenance import get_provenance_payload


def score_confidence(level: str) -> float:
    mapping = {
        "official": 1.0,
        "exact": 0.98,
        "computed": 0.9,
        "astronomical": 0.95,
        "estimated": 0.7,
        "unknown": 0.5,
    }
    return mapping.get((level or "unknown").lower(), 0.5)


def to_v5_confidence_level(level: str) -> str:
    normalized = (level or "unknown").lower()
    if normalized in {"official", "estimated"}:
        return normalized
    if normalized in {"computed", "exact", "astronomical"}:
        return "computed"
    return "unknown"


def derive_boundary_risk(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "unknown"
    tithi = payload.get("tithi")
    if not isinstance(tithi, dict):
        return "unknown"
    uncertainty = tithi.get("uncertainty")
    if not isinstance(uncertainty, dict):
        return "unknown"

    confidence = str(uncertainty.get("confidence", "")).lower()
    if confidence in {"exact", "high"}:
        return "low"
    if confidence in {"medium", "computed"}:
        return "medium"
    if confidence in {"low", "estimated"}:
        return "high"
    return "unknown"


def derive_signature(provenance: dict[str, Any]) -> str | None:
    snapshot_id = provenance.get("snapshot_id")
    dataset_hash = provenance.get("dataset_hash")
    rules_hash = provenance.get("rules_hash")
    if not snapshot_id or not dataset_hash or not rules_hash:
        return None

    seed = f"{snapshot_id}:{dataset_hash}:{rules_hash}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return f"sha256sig:{digest[:40]}"


def merge_meta_defaults(defaults: dict[str, Any], provided: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(defaults)
    for key, value in provided.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_meta_defaults(merged[key], value)
        else:
            merged[key] = value
    return merged


def extract_meta(payload: Any, *, track: str = "v4") -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "confidence": "computed",
            "method": "unknown",
            "provenance": {},
            "uncertainty": {"level": "unknown", "interval_hours": None},
            "trace_id": None,
        }

    tithi_block = payload.get("tithi") if isinstance(payload.get("tithi"), dict) else {}
    bs_block = payload.get("bikram_sambat") if isinstance(payload.get("bikram_sambat"), dict) else {}
    panchanga_block = payload.get("panchanga") if isinstance(payload.get("panchanga"), dict) else {}

    confidence_level_raw = (
        payload.get("confidence")
        or tithi_block.get("confidence")
        or bs_block.get("confidence")
        or panchanga_block.get("confidence")
        or "unknown"
    )
    confidence_level = str(confidence_level_raw).lower()
    method = payload.get("method") or tithi_block.get("method") or payload.get("engine_version") or "unknown"

    verify_url = "/v5/api/provenance/root" if track == "v5" else "/v4/api/provenance/root"
    fallback_provenance = get_provenance_payload(verify_url=verify_url, create_if_missing=True)
    raw_provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    provenance = merge_meta_defaults(fallback_provenance, raw_provenance)

    signature = derive_signature(provenance)
    if "signature" not in provenance:
        provenance = {**provenance, "signature": signature}

    uncertainty = payload.get("uncertainty")
    if not isinstance(uncertainty, dict):
        uncertainty = {"interval_hours": None, "boundary_risk": derive_boundary_risk(payload)}

    trace_id = (
        payload.get("calculation_trace_id")
        or payload.get("trace_id")
        or (payload.get("trace", {}).get("trace_id") if isinstance(payload.get("trace"), dict) else None)
    )

    if track == "v5":
        v5_confidence_level = to_v5_confidence_level(confidence_level)
        confidence = {
            "level": v5_confidence_level,
            "score": score_confidence(v5_confidence_level),
        }
        return {
            "confidence": confidence,
            "method": method,
            "provenance": provenance,
            "uncertainty": {
                "interval_hours": uncertainty.get("interval_hours"),
                "boundary_risk": uncertainty.get("boundary_risk", derive_boundary_risk(payload)),
            },
            "trace_id": trace_id,
            "policy": {
                "profile": "np-mainstream",
                "jurisdiction": "NP",
                "advisory": True,
            },
        }

    return {
        "confidence": confidence_level,
        "method": method,
        "provenance": provenance,
        "uncertainty": uncertainty,
        "trace_id": trace_id,
    }
