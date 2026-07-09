"""Near-boundary risk scoring for civil month-start assignment."""

from __future__ import annotations

from typing import Any


def boundary_risk_label(distance_minutes: int | None) -> str:
    if distance_minutes is None:
        return "low"
    if distance_minutes < 30:
        return "critical"
    if distance_minutes < 120:
        return "high"
    if distance_minutes < 360:
        return "medium"
    return "low"


def boundary_risk_payload(distance_minutes: int | None) -> dict[str, Any]:
    label = boundary_risk_label(distance_minutes)
    flags: list[str] = []
    if label in {"critical", "high"}:
        flags.extend(["sankranti_near_civil_assignment_boundary", "manual_review_recommended"])
    elif label == "medium":
        flags.append("sankranti_moderately_near_civil_assignment_boundary")
    return {
        "boundary_distance_minutes": distance_minutes,
        "boundary_risk": label,
        "risk_flags": flags,
    }
