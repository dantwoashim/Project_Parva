"""File-backed implementations of storage abstractions."""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from app.provenance.attestation import build_attestation, verify_attestation

from .interfaces import TraceStore, TransparencyLogStore


def _canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class FileTraceStore(TraceStore):
    def __init__(
        self,
        trace_dir: Path,
        *,
        public_trace_types: frozenset[str],
        private_ttl_hours: int,
    ) -> None:
        self.trace_dir = trace_dir
        self.public_trace_types = public_trace_types
        self.private_ttl_hours = private_ttl_hours

    def _trace_id(self, payload: dict[str, Any]) -> str:
        digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
        return f"tr_{digest[:20]}"

    def _private_trace_id(self) -> str:
        return f"tr_{secrets.token_hex(10)}"

    def _default_visibility(self, trace_type: str) -> str:
        return "public" if trace_type in self.public_trace_types else "private"

    def _redact_private_inputs(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return {key: "[redacted]" for key in inputs}

    def _redact_private_subject(self, subject: dict[str, Any]) -> dict[str, Any]:
        return {"label": "private_trace"} if subject else {}

    def create(
        self,
        *,
        trace_type: str,
        subject: dict[str, Any],
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        steps: list[dict[str, Any]],
        provenance: dict[str, Any] | None = None,
        visibility: str | None = None,
    ) -> dict[str, Any]:
        normalized_visibility = visibility or self._default_visibility(trace_type)
        is_public = normalized_visibility == "public"
        base_payload = {
            "trace_type": trace_type,
            "visibility": normalized_visibility,
            "subject": subject if is_public else self._redact_private_subject(subject),
            "inputs": inputs if is_public else self._redact_private_inputs(inputs),
            "outputs": outputs,
            "steps": steps,
            "provenance": provenance or {},
            "redacted": not is_public,
            "retention_ttl_hours": None if is_public else self.private_ttl_hours,
        }
        trace_id = self._trace_id(base_payload) if is_public else self._private_trace_id()
        payload = {
            "trace_id": trace_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **base_payload,
        }
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        (self.trace_dir / f"{trace_id}.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return payload

    def get(self, trace_id: str, *, include_private: bool = False) -> dict[str, Any] | None:
        path = self.trace_dir / f"{trace_id}.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        if not include_private and payload.get("visibility") != "public":
            return None
        return payload

    def list_recent(
        self, limit: int = 20, *, include_private: bool = False
    ) -> list[dict[str, Any]]:
        files = sorted(
            self.trace_dir.glob("tr_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]
        rows: list[dict[str, Any]] = []
        for path in files:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
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
        return rows


class FileTransparencyLogStore(TransparencyLogStore):
    def __init__(self, *, transparency_dir: Path, log_path: Path, anchor_path: Path) -> None:
        self.transparency_dir = transparency_dir
        self.log_path = log_path
        self.anchor_path = anchor_path

    def _ensure_dir(self) -> None:
        self.transparency_dir.mkdir(parents=True, exist_ok=True)

    def load_entries(self) -> list[dict[str, Any]]:
        self._ensure_dir()
        if not self.log_path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(json.loads(line))
        return rows

    def append_entry(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        self._ensure_dir()
        entries = self.load_entries()
        now = datetime.now(timezone.utc)
        entry_id = f"tle_{now.strftime('%Y%m%dT%H%M%S%fZ')}"
        timestamp = now.isoformat()
        prev_hash = str(entries[-1].get("entry_hash") if entries else "GENESIS")
        body = {
            "entry_id": entry_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "payload": payload,
            "prev_hash": prev_hash,
        }
        entry_hash = _sha256_hex(_canonical(body))
        attestation = build_attestation({**body, "entry_hash": entry_hash})
        entry = {**body, "entry_hash": entry_hash, "attestation": attestation}
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def verify_integrity(self) -> dict[str, Any]:
        entries = self.load_entries()
        checks: list[dict[str, Any]] = []
        prev_hash = "GENESIS"
        valid = True
        for idx, row in enumerate(entries):
            body = {
                "entry_id": str(row.get("entry_id")),
                "timestamp": str(row.get("timestamp")),
                "event_type": str(row.get("event_type")),
                "payload": dict(row.get("payload") or {}),
                "prev_hash": str(row.get("prev_hash")),
            }
            expected_hash = _sha256_hex(_canonical(body))
            attestation = row.get("attestation")
            hash_ok = expected_hash == str(row.get("entry_hash"))
            chain_ok = str(row.get("prev_hash")) == prev_hash
            if isinstance(attestation, dict):
                attestation_ok = verify_attestation(
                    {**body, "entry_hash": str(row.get("entry_hash"))},
                    attestation,
                )
                attestation_mode = str(attestation.get("mode") or "unknown")
            else:
                attestation_ok = False
                attestation_mode = "missing"
            row_ok = hash_ok and chain_ok and attestation_ok
            if not row_ok:
                valid = False
            checks.append(
                {
                    "index": idx,
                    "entry_id": row.get("entry_id"),
                    "hash_ok": hash_ok,
                    "chain_ok": chain_ok,
                    "attestation_ok": attestation_ok,
                    "attestation_mode": attestation_mode,
                }
            )
            prev_hash = str(row.get("entry_hash"))
        return {
            "valid": valid,
            "total_entries": len(entries),
            "head_hash": prev_hash,
            "checks": checks,
        }

    def replay_state(self) -> dict[str, Any]:
        entries = self.load_entries()
        latest_snapshot: Optional[Dict[str, Any]] = None
        by_event: Dict[str, int] = {}
        for row in entries:
            event = str(row.get("event_type") or "unknown")
            by_event[event] = by_event.get(event, 0) + 1
            if event == "snapshot_created":
                latest_snapshot = dict(row.get("payload") or {})
        return {
            "total_entries": len(entries),
            "event_counts": by_event,
            "latest_snapshot": latest_snapshot,
            "head_hash": entries[-1]["entry_hash"] if entries else "GENESIS",
        }

    def record_anchor(
        self,
        tx_ref: str,
        network: str,
        payload: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        self._ensure_dir()
        anchor = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "network": network,
            "tx_ref": tx_ref,
            "payload": payload or {},
        }
        with self.anchor_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(anchor, ensure_ascii=False) + "\n")
        return anchor

    def list_anchors(self, limit: int = 50) -> list[dict[str, Any]]:
        self._ensure_dir()
        if not self.anchor_path.exists():
            return []
        rows = [
            json.loads(line)
            for line in self.anchor_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        return rows[-max(1, limit) :]
