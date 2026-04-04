"""Reason-trace store with public/private visibility controls."""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRACE_DIR = PROJECT_ROOT / "backend" / "data" / "traces"
PUBLIC_TRACE_TYPES = frozenset(
    {
        "festival_date_explain",
        "festival_timeline",
    }
)
PRIVATE_TRACE_TTL_HOURS = 168


def _canonical(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _trace_id(payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return f"tr_{digest[:20]}"


def _private_trace_id() -> str:
    return f"tr_{secrets.token_hex(10)}"


def _default_visibility(trace_type: str) -> str:
    return "public" if trace_type in PUBLIC_TRACE_TYPES else "private"


def _redact_private_inputs(inputs: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key in inputs:
        redacted[key] = "[redacted]"
    return redacted


def _redact_private_subject(subject: dict[str, Any]) -> dict[str, Any]:
    if not subject:
        return {}
    return {"label": "private_trace"}


def create_reason_trace(
    *,
    trace_type: str,
    subject: dict[str, Any],
    inputs: dict[str, Any],
    outputs: dict[str, Any],
    steps: list[dict[str, Any]],
    provenance: dict[str, Any] | None = None,
    visibility: str | None = None,
) -> dict[str, Any]:
    """
    Create and persist a reason trace.

    Public traces remain deterministic and retrievable for transparent festival-style
    explainability. Sensitive personal/location traces are stored with opaque ids,
    redacted persisted inputs, and private visibility by default.
    """
    normalized_visibility = visibility or _default_visibility(trace_type)
    is_public = normalized_visibility == "public"
    base_payload = {
        "trace_type": trace_type,
        "visibility": normalized_visibility,
        "subject": subject if is_public else _redact_private_subject(subject),
        "inputs": inputs if is_public else _redact_private_inputs(inputs),
        "outputs": outputs,
        "steps": steps,
        "provenance": provenance or {},
        "redacted": not is_public,
        "retention_ttl_hours": None if is_public else PRIVATE_TRACE_TTL_HOURS,
    }
    trace_id = _trace_id(base_payload) if is_public else _private_trace_id()
    payload = {
        "trace_id": trace_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **base_payload,
    }
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    (TRACE_DIR / f"{trace_id}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return payload


def get_reason_trace(trace_id: str, *, include_private: bool = False) -> dict[str, Any] | None:
    path = TRACE_DIR / f"{trace_id}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not include_private and payload.get("visibility") != "public":
        return None
    return payload


def list_recent_traces(limit: int = 20, *, include_private: bool = False) -> list[dict[str, Any]]:
    files = sorted(TRACE_DIR.glob("tr_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[
        :limit
    ]
    rows: list[dict[str, Any]] = []
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not include_private and payload.get("visibility") != "public":
                continue
            rows.append(
                {
                    "trace_id": payload.get("trace_id"),
                    "trace_type": payload.get("trace_type"),
                    "visibility": payload.get("visibility", "private"),
                    "subject": payload.get("subject"),
                    "created_at": payload.get("created_at"),
                }
            )
        except Exception:
            continue
    return rows
