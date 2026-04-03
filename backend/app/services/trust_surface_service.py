"""Shared trust/risk helpers for portable proof-capsule surfaces."""

from __future__ import annotations

from typing import Any

from app.festivals.risk_service import truth_ladder


def _normalize_progress(progress: Any) -> float | None:
    try:
        value = float(progress)
    except (TypeError, ValueError):
        return None
    if 0.0 <= value <= 1.0:
        return value
    if 0.0 <= value <= 100.0:
        return value / 100.0
    return None


def build_temporal_risk_payload(
    *,
    progress: Any,
    support_tier: str,
    fallback_used: bool,
    method: str,
    risk_mode: str = "standard",
) -> dict[str, Any]:
    normalized_method = str(method or "").strip().lower()
    normalized_tier = str(support_tier or "").strip().lower()
    normalized_mode = str(risk_mode or "standard").strip().lower()
    progress_value = _normalize_progress(progress)

    if progress_value is not None:
        distance = min(progress_value, 1.0 - progress_value)
        if distance <= 0.08:
            boundary_radar = "high_disagreement_risk"
        elif distance <= 0.18:
            boundary_radar = "one_day_sensitive"
        else:
            boundary_radar = "stable"
    elif normalized_method == "instantaneous":
        boundary_radar = "one_day_sensitive"
    elif fallback_used or normalized_tier in {"heuristic", "estimated", "conflicted"}:
        boundary_radar = "one_day_sensitive"
    else:
        boundary_radar = "stable"

    stability_score = {
        "authoritative": 0.97,
        "computed": 0.86,
        "heuristic": 0.62,
        "estimated": 0.5,
        "conflicted": 0.48,
    }.get(normalized_tier, 0.7)

    if normalized_method == "instantaneous":
        stability_score -= 0.12
    if fallback_used:
        stability_score -= 0.1
    if progress_value is not None:
        distance = min(progress_value, 1.0 - progress_value)
        if distance <= 0.08:
            stability_score -= 0.28
        elif distance <= 0.18:
            stability_score -= 0.14
    stability_score = round(min(max(stability_score, 0.05), 0.99), 2)

    abstained = normalized_mode == "strict" and boundary_radar == "high_disagreement_risk"
    if abstained:
        recommended_action = (
            "Strict mode abstained because this result sits near a temporal boundary. "
            "Retry with explicit location/timezone and compare alternate authority surfaces."
        )
    elif boundary_radar == "high_disagreement_risk":
        recommended_action = (
            "Treat this as boundary-sensitive and verify before ritual-critical use."
        )
    elif boundary_radar == "one_day_sensitive":
        recommended_action = (
            "Keep explicit location/timezone attached because this result may shift by a day."
        )
    elif fallback_used or normalized_tier in {"heuristic", "estimated"}:
        recommended_action = (
            "Use this directionally and verify against published calendars before hard commitments."
        )
    else:
        recommended_action = "This result is stable enough for routine planning."

    return {
        "boundary_radar": boundary_radar,
        "stability_score": stability_score,
        "risk_mode": normalized_mode,
        "abstained": abstained,
        "recommended_action": recommended_action,
    }


def build_portable_proof_capsule(
    *,
    surface: str,
    payload: dict[str, Any],
    request: dict[str, Any],
    source_lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tithi = payload.get("tithi") or ((payload.get("panchanga") or {}).get("tithi") or {})
    lineage = {
        "method": payload.get("method") or tithi.get("method"),
        "confidence": payload.get("confidence") or tithi.get("confidence"),
        "reference_time": tithi.get("reference_time"),
        "sunrise_used": tithi.get("sunrise_used"),
        "service_status": payload.get("service_status"),
        "cache": payload.get("cache"),
    }
    if source_lineage:
        lineage.update(source_lineage)
    return {
        "surface": surface,
        "request": request,
        "selection": {
            "date": payload.get("date") or payload.get("gregorian"),
            "support_tier": payload.get("support_tier"),
            "engine_path": payload.get("engine_path"),
            "fallback_used": payload.get("fallback_used"),
            "calibration_status": payload.get("calibration_status"),
            "abstained": payload.get("abstained", False),
        },
        "source_lineage": lineage,
        "risk": {
            "boundary_radar": payload.get("boundary_radar"),
            "stability_score": payload.get("stability_score"),
            "risk_mode": payload.get("risk_mode"),
            "recommended_action": payload.get("recommended_action"),
            "truth_ladder": truth_ladder(),
        },
        "provenance": payload.get("provenance"),
        "policy": payload.get("policy"),
        "calculation_trace_id": payload.get("calculation_trace_id"),
    }

