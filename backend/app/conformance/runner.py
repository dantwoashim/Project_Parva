"""Run conformance capsules from local data."""

from __future__ import annotations

from app.workflows.date_risk_audit import audit_date_rows


def run_conformance_capsule(capsule: dict) -> dict:
    rows = capsule.get("cases", [])
    return {
        "capsule_id": capsule.get("capsule_id"),
        "workflow": capsule.get("workflow"),
        "claim_boundary": "conformance_report_not_certification",
        "results": audit_date_rows(rows),
    }
