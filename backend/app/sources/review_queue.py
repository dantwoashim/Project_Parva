"""Review-driven source ingestion queue helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MOHA_INVENTORY_PATH = PROJECT_ROOT / "data" / "source_inventory" / "moha_official_years.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}


def _resolve_path(path_str: str | None) -> Path | None:
    if not path_str:
        return None
    candidate = PROJECT_ROOT / path_str
    return candidate


def _review_action_for_status(status: str, *, local_exists: bool, structured_count: int) -> tuple[str, str, list[str]]:
    normalized = str(status or "").strip().lower()
    reasons: list[str] = []

    if not local_exists:
        reasons.append("local_source_missing")
        return "reacquire_source", "critical", reasons

    if normalized == "archived_raw_pdf":
        reasons.append("structured_artifacts_missing")
        return "improve_extraction", "high", reasons

    if normalized == "structured_official" and structured_count == 0:
        reasons.append("inventory_claims_structured_but_no_artifacts_listed")
        return "audit_structured_artifacts", "high", reasons

    if normalized == "structured_official":
        reasons.append("ready_for_human_review")
        return "review_and_promote", "medium", reasons

    reasons.append("unclassified_source_status")
    return "inventory_review", "medium", reasons


def build_source_review_queue() -> dict[str, Any]:
    inventory = _read_json(MOHA_INVENTORY_PATH)
    rows = inventory.get("sources", []) if isinstance(inventory.get("sources"), list) else []
    queue: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        local_path = _resolve_path(row.get("local_path"))
        structured_artifacts = [
            artifact
            for artifact in (row.get("structured_artifacts") or [])
            if isinstance(artifact, str) and artifact.strip()
        ]
        local_exists = bool(local_path and local_path.exists())
        structured_existing = [
            artifact
            for artifact in structured_artifacts
            if (PROJECT_ROOT / artifact).exists()
        ]
        action, priority, reasons = _review_action_for_status(
            str(row.get("status") or ""),
            local_exists=local_exists,
            structured_count=len(structured_artifacts),
        )

        queue.append(
            {
                "source_family": "moha_official",
                "source_id": f"moha_official_{row.get('bs_year')}",
                "bs_year": row.get("bs_year"),
                "status": row.get("status"),
                "source_type": row.get("source_type"),
                "url": row.get("url"),
                "local_path": row.get("local_path"),
                "local_path_exists": local_exists,
                "structured_artifacts": structured_artifacts,
                "structured_artifact_count": len(structured_artifacts),
                "structured_artifacts_existing": structured_existing,
                "review_action": action,
                "review_priority": priority,
                "ready_for_promotion": action == "review_and_promote" and bool(structured_existing),
                "notes": row.get("notes"),
                "reasons": reasons,
            }
        )

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    queue.sort(key=lambda item: (priority_order.get(item["review_priority"], 9), item.get("bs_year") or 0))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_family": "moha_official",
        "inventory_path": str(MOHA_INVENTORY_PATH.relative_to(PROJECT_ROOT)),
        "total_items": len(queue),
        "summary": {
            "critical": sum(1 for item in queue if item["review_priority"] == "critical"),
            "high": sum(1 for item in queue if item["review_priority"] == "high"),
            "medium": sum(1 for item in queue if item["review_priority"] == "medium"),
            "ready_for_promotion": sum(1 for item in queue if item["ready_for_promotion"]),
        },
        "items": queue,
    }


__all__ = ["build_source_review_queue"]
