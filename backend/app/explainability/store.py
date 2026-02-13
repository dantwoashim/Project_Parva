"""Deterministic reason-trace store for explainability endpoints."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRACE_DIR = PROJECT_ROOT / "backend" / "data" / "traces"


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _trace_id(payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return f"tr_{digest[:20]}"


def create_reason_trace(
    *,
    trace_type: str,
    subject: dict[str, Any],
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    steps: list[dict[str, Any]],
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create and persist a deterministic reason trace.

    Trace id is derived from canonical payload (excluding created_at), so repeated
    calculations with identical inputs/rules produce the same trace id.
    """
    base_payload = {
        "trace_type": trace_type,
        "subject": subject,
        "inputs": inputs,
        "outputs": outputs,
        "steps": steps,
        "provenance": provenance or {},
    }
    trace_id = _trace_id(base_payload)
    payload = {
        "trace_id": trace_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **base_payload,
    }
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    (TRACE_DIR / f"{trace_id}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload


def get_reason_trace(trace_id: str) -> dict[str, Any] | None:
    path = TRACE_DIR / f"{trace_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def list_recent_traces(limit: int = 20) -> list[dict[str, Any]]:
    files = sorted(TRACE_DIR.glob("tr_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    rows: list[dict[str, Any]] = []
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "trace_id": payload.get("trace_id"),
                    "trace_type": payload.get("trace_type"),
                    "subject": payload.get("subject"),
                    "created_at": payload.get("created_at"),
                }
            )
        except Exception:
            continue
    return rows
