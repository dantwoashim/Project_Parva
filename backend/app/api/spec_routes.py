"""Spec and conformance visibility endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter

from app.core.paths import project_root, resolve_resource_path

router = APIRouter(prefix="/api/spec", tags=["spec"])

PROJECT_ROOT = project_root()
CONFORMANCE_REPORT = resolve_resource_path(
    "PARVA_CONFORMANCE_REPORT",
    Path("reports") / "conformance_report.json",
)
SPEC_DOC = resolve_resource_path(
    "PARVA_TEMPORAL_SPEC_DOC",
    Path("docs") / "spec" / "PARVA_TEMPORAL_SPEC_V1.md",
)
CONFORMANCE_CASES = resolve_resource_path(
    "PARVA_CONFORMANCE_CASES",
    Path("tests") / "conformance" / "conformance_cases.v1.json",
)


@router.get("/conformance")
async def get_conformance_status():
    """Expose conformance status with report + case pack metadata."""
    report = None
    report_exists = CONFORMANCE_REPORT.exists()
    if report_exists:
        report = json.loads(CONFORMANCE_REPORT.read_text(encoding="utf-8"))

    case_count = 0
    if CONFORMANCE_CASES.exists():
        try:
            case_payload = json.loads(CONFORMANCE_CASES.read_text(encoding="utf-8"))
            case_count = len(case_payload.get("cases", []))
        except (OSError, json.JSONDecodeError):
            case_count = 0

    return {
        "spec": {
            "version": "1.0",
            "path": str(SPEC_DOC.relative_to(PROJECT_ROOT)),
            "exists": SPEC_DOC.exists(),
        },
        "conformance": report,
        "report_exists": report_exists,
        "case_pack": {
            "path": str(CONFORMANCE_CASES.relative_to(PROJECT_ROOT)),
            "exists": CONFORMANCE_CASES.exists(),
            "cases": case_count,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
