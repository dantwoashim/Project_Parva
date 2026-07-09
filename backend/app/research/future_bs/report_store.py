"""Artifact-first report store for future BS and model-risk reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.research.future_bs.paths import project_root

PROJECT_ROOT = project_root()

REPORTS: dict[str, tuple[str, str]] = {
    "claim_readiness_v_final": (
        "data/future_bs/reports/claim_readiness_v_final.json",
        "python scripts/future_bs/generate_all_final_artifacts.py",
    ),
    "case_2083_ashwin_replay_v_final": (
        "data/future_bs/reports/case_2083_ashwin_replay_v_final.json",
        "python scripts/future_bs/generate_all_final_artifacts.py",
    ),
    "time_travel_official_v_final": (
        "data/future_bs/reports/time_travel_official_v_final.json",
        "python scripts/future_bs/generate_all_final_artifacts.py",
    ),
    "invalid_year_total_reconciliation_v_final": (
        "data/future_bs/reports/invalid_year_total_reconciliation_v_final.json",
        "python scripts/future_bs/generate_all_final_artifacts.py",
    ),
    "parva_calendar_var_sample_v_final": (
        "data/future_bs/reports/parva_calendar_var_sample_v_final.json",
        "python scripts/future_bs/generate_all_final_artifacts.py",
    ),
    "external_audit_readiness_summary": (
        "data/future_bs/external_audit_ready/PARVA_EXTERNAL_AUDIT_READINESS_SUMMARY.json",
        "python scripts/future_bs/generate_all_final_artifacts.py",
    ),
}


def report_path(report_id: str) -> Path:
    try:
        relative, _ = REPORTS[report_id]
    except KeyError as exc:
        raise ValueError(f"Unknown report_id: {report_id}") from exc
    return PROJECT_ROOT / relative


def report_exists(report_id: str) -> bool:
    path = report_path(report_id)
    return path.exists() and path.stat().st_size > 0


def missing_report_payload(report_id: str, command: str | None = None) -> dict[str, Any]:
    if report_id in REPORTS:
        default_command = REPORTS[report_id][1]
    else:
        default_command = "python scripts/future_bs/generate_all_final_artifacts.py"
    return {
        "error": "report_not_generated",
        "report_id": report_id,
        "command": command or default_command,
        "publication_status": "computed_prediction_not_official",
    }


def load_report(report_id: str) -> dict[str, Any]:
    if not report_exists(report_id):
        return missing_report_payload(report_id)
    path = report_path(report_id)
    return json.loads(path.read_text(encoding="utf-8"))


def save_report(report_id: str, payload: dict[str, Any]) -> None:
    path = report_path(report_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def list_reports() -> dict[str, Any]:
    return {
        "publication_status": "computed_prediction_not_official",
        "reports": {
            report_id: {
                "path": str(report_path(report_id).relative_to(PROJECT_ROOT)),
                "exists": report_exists(report_id),
                "command": command,
            }
            for report_id, (_, command) in REPORTS.items()
        },
    }
