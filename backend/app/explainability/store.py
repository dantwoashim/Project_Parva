"""Reason-trace store with public/private visibility controls."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.storage.file_stores import FileTraceStore

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRACE_DIR = PROJECT_ROOT / "backend" / "data" / "traces"
PUBLIC_TRACE_TYPES = frozenset(
    {
        "festival_date_explain",
        "festival_timeline",
    }
)
PRIVATE_TRACE_TTL_HOURS = 168

def get_trace_store() -> FileTraceStore:
    return FileTraceStore(
        TRACE_DIR,
        public_trace_types=PUBLIC_TRACE_TYPES,
        private_ttl_hours=PRIVATE_TRACE_TTL_HOURS,
    )


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
    return get_trace_store().create(
        trace_type=trace_type,
        subject=subject,
        inputs=inputs,
        outputs=outputs,
        steps=steps,
        provenance=provenance,
        visibility=visibility,
    )


def get_reason_trace(trace_id: str, *, include_private: bool = False) -> dict[str, Any] | None:
    return get_trace_store().get(trace_id, include_private=include_private)


def list_recent_traces(limit: int = 20, *, include_private: bool = False) -> list[dict[str, Any]]:
    return get_trace_store().list_recent(limit=limit, include_private=include_private)
