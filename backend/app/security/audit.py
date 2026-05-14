"""Structured security audit helpers."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request

from app.security.pii import scrub_structured_trace

security_audit_logger = logging.getLogger("parva.security.audit")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_AUDIT_LOG_PATH = PROJECT_ROOT / "data" / "security_audit" / "admin_mutations.jsonl"
_AUDIT_LOG_LOCK = threading.Lock()


def canonical_audit_hash(payload: Any) -> str | None:
    if payload is None:
        return None
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def request_audit_context(request: Request) -> dict[str, Any]:
    principal = getattr(request.state, "principal", None)
    return {
        "actor_principal": getattr(principal, "principal_id", None),
        "actor_type": getattr(principal, "principal_type", None),
        "route": request.url.path,
        "request_id": getattr(request.state, "request_id", None),
        "source_ip": getattr(request.state, "client_ip", None),
    }


def emit_security_audit_event(
    request: Request,
    *,
    action: str,
    object_type: str,
    object_id: str | None,
    before: Any = None,
    after: Any = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "event": "security.admin_mutation",
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "before_hash": canonical_audit_hash(before),
        "after_hash": canonical_audit_hash(after),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **request_audit_context(request),
        "metadata": scrub_structured_trace(metadata or {}),
    }
    security_audit_logger.info(json.dumps(payload, sort_keys=True))
    path = Path(os.getenv("PARVA_SECURITY_AUDIT_LOG", "") or DEFAULT_AUDIT_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _AUDIT_LOG_LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return payload
