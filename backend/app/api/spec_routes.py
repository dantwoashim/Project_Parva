"""Spec and conformance visibility endpoints."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter


router = APIRouter(prefix="/api/spec", tags=["spec"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFORMANCE_REPORT = PROJECT_ROOT / "reports" / "conformance_report.json"
SPEC_DOC = PROJECT_ROOT / "docs" / "spec" / "PARVA_TEMPORAL_SPEC_V1.md"
CONFORMANCE_CASES = PROJECT_ROOT / "tests" / "conformance" / "conformance_cases.v1.json"


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
        except Exception:
            case_count = 0

    return {
        "spec": {
            "version": "1.0",
            "path": str(SPEC_DOC),
            "exists": SPEC_DOC.exists(),
        },
        "conformance": report,
        "report_exists": report_exists,
        "case_pack": {
            "path": str(CONFORMANCE_CASES),
            "exists": CONFORMANCE_CASES.exists(),
            "cases": case_count,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
