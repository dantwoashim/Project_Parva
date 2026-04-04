"""Shared trust/risk helpers for portable proof-capsule surfaces."""

from __future__ import annotations

from typing import Any

from app.core.request_context import derive_support_tier
from app.domain.temporal_context import CalendarContext, LocationContext
from app.policy import get_policy_metadata
from app.provenance import get_latest_snapshot, get_provenance_payload


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


def build_surface_meta(
    *,
    engine_path: str,
    confidence: str,
    quality_band: str,
    uncertainty: dict[str, Any] | None = None,
    fallback_used: bool | None = None,
) -> dict[str, Any]:
    calibration_mode = None
    if isinstance(uncertainty, dict):
        calibration_mode = str(uncertainty.get("calibration_mode") or "").strip().lower()
    return {
        "support_tier": derive_support_tier(
            confidence=confidence,
            quality_band=quality_band,
        ),
        "engine_path": engine_path,
        "fallback_used": (
            ("fallback" in engine_path.lower()) or ("legacy" in engine_path.lower())
            if fallback_used is None
            else fallback_used
        ),
        "calibration_status": "empirical" if calibration_mode == "empirical" else "unavailable",
    }


def build_surface_provenance(
    *,
    festival_id: str | None = None,
    year: int | None = None,
    calendar_context: CalendarContext | None = None,
    create_if_missing: bool = True,
) -> dict[str, Any]:
    snapshot = get_latest_snapshot(create_if_missing=create_if_missing)
    snapshot_id = snapshot.snapshot_id if snapshot else None
    verify_url = "/v3/api/provenance/root"
    if festival_id and year and snapshot_id:
        verify_url = (
            f"/v3/api/provenance/proof?festival={festival_id}&year={year}&snapshot={snapshot_id}"
        )
    payload = get_provenance_payload(verify_url=verify_url, create_if_missing=create_if_missing)
    if calendar_context is not None:
        payload["calendar_context"] = calendar_context.as_dict()
    return payload


def build_surface_presentation(
    *,
    engine_path: str,
    confidence: str,
    quality_band: str,
    uncertainty: dict[str, Any] | None = None,
    progress: Any = None,
    method: str | None = None,
    risk_mode: str = "standard",
    fallback_used: bool | None = None,
    calendar_context: CalendarContext | None = None,
    festival_id: str | None = None,
    year: int | None = None,
) -> dict[str, Any]:
    meta = build_surface_meta(
        engine_path=engine_path,
        confidence=confidence,
        quality_band=quality_band,
        uncertainty=uncertainty,
        fallback_used=fallback_used,
    )
    if calendar_context is not None:
        calendar_context = CalendarContext(
            target_date=calendar_context.target_date,
            surface=calendar_context.surface,
            risk_mode=calendar_context.risk_mode,
            snapshot_id=calendar_context.snapshot_id,
            support_tier=str(meta["support_tier"]),
            calendar_system=calendar_context.calendar_system,
        )
    risk = build_temporal_risk_payload(
        progress=progress,
        support_tier=str(meta["support_tier"]),
        fallback_used=bool(meta["fallback_used"]),
        method=method or engine_path,
        risk_mode=risk_mode,
    )
    return {
        **meta,
        **risk,
        "provenance": build_surface_provenance(
            festival_id=festival_id,
            year=year,
            calendar_context=calendar_context,
            create_if_missing=True,
        ),
        "policy": get_policy_metadata(),
    }


def build_portable_proof_capsule(
    *,
    surface: str,
    payload: dict[str, Any],
    request: dict[str, Any],
    source_lineage: dict[str, Any] | None = None,
    calendar_context: CalendarContext | None = None,
    location_context: LocationContext | None = None,
) -> dict[str, Any]:
    from app.festivals.risk_service import truth_ladder

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
        "calendar_context": (
            calendar_context.as_dict()
            if calendar_context is not None
            else (payload.get("provenance") or {}).get("calendar_context")
        ),
        "location_context": (
            location_context.as_dict()
            if location_context is not None
            else payload.get("location_context")
        ),
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
