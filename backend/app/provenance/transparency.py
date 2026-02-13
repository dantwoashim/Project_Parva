"""Append-only transparency log for provenance snapshots and rule changes."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRANSPARENCY_DIR = PROJECT_ROOT / "data" / "transparency"
TRANSPARENCY_LOG = TRANSPARENCY_DIR / "log.jsonl"
ANCHOR_LOG = TRANSPARENCY_DIR / "anchors.jsonl"


@dataclass
class TransparencyEntry:
    entry_id: str
    timestamp: str
    event_type: str
    payload: Dict[str, Any]
    prev_hash: str
    entry_hash: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
            "signature": self.signature,
        }


def _canonical(value: Dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _entry_body(
    *,
    entry_id: str,
    timestamp: str,
    event_type: str,
    payload: Dict[str, Any],
    prev_hash: str,
) -> Dict[str, Any]:
    return {
        "entry_id": entry_id,
        "timestamp": timestamp,
        "event_type": event_type,
        "payload": payload,
        "prev_hash": prev_hash,
    }


def _ensure_dir() -> None:
    TRANSPARENCY_DIR.mkdir(parents=True, exist_ok=True)


def load_log_entries() -> List[Dict[str, Any]]:
    _ensure_dir()
    if not TRANSPARENCY_LOG.exists():
        return []
    rows: List[Dict[str, Any]] = []
    for line in TRANSPARENCY_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _last_hash(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return "GENESIS"
    return str(entries[-1].get("entry_hash") or "GENESIS")


def append_entry(event_type: str, payload: Dict[str, Any]) -> TransparencyEntry:
    _ensure_dir()
    entries = load_log_entries()

    now = _now_utc()
    entry_id = f"tle_{now.strftime('%Y%m%dT%H%M%S%fZ')}"
    timestamp = now.isoformat()
    prev_hash = _last_hash(entries)

    body = _entry_body(
        entry_id=entry_id,
        timestamp=timestamp,
        event_type=event_type,
        payload=payload,
        prev_hash=prev_hash,
    )
    entry_hash = _sha256_hex(_canonical(body))
    signature = f"sha256:{entry_hash}"

    entry = TransparencyEntry(
        entry_id=entry_id,
        timestamp=timestamp,
        event_type=event_type,
        payload=payload,
        prev_hash=prev_hash,
        entry_hash=entry_hash,
        signature=signature,
    )

    with TRANSPARENCY_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    return entry


def append_snapshot_event(snapshot_id: str, dataset_hash: str, rules_hash: str) -> TransparencyEntry:
    return append_entry(
        "snapshot_created",
        {
            "snapshot_id": snapshot_id,
            "dataset_hash": dataset_hash,
            "rules_hash": rules_hash,
        },
    )


def verify_log_integrity() -> Dict[str, Any]:
    entries = load_log_entries()
    checks: List[Dict[str, Any]] = []

    prev_hash = "GENESIS"
    valid = True

    for idx, row in enumerate(entries):
        body = _entry_body(
            entry_id=str(row.get("entry_id")),
            timestamp=str(row.get("timestamp")),
            event_type=str(row.get("event_type")),
            payload=dict(row.get("payload") or {}),
            prev_hash=str(row.get("prev_hash")),
        )
        expected_hash = _sha256_hex(_canonical(body))

        hash_ok = expected_hash == str(row.get("entry_hash"))
        chain_ok = str(row.get("prev_hash")) == prev_hash
        sig_ok = str(row.get("signature")) == f"sha256:{row.get('entry_hash')}"
        row_ok = hash_ok and chain_ok and sig_ok
        if not row_ok:
            valid = False

        checks.append(
            {
                "index": idx,
                "entry_id": row.get("entry_id"),
                "hash_ok": hash_ok,
                "chain_ok": chain_ok,
                "signature_ok": sig_ok,
            }
        )

        prev_hash = str(row.get("entry_hash"))

    return {
        "valid": valid,
        "total_entries": len(entries),
        "head_hash": prev_hash,
        "checks": checks,
    }


def replay_state() -> Dict[str, Any]:
    entries = load_log_entries()
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


def prepare_anchor_payload(note: str = "") -> Dict[str, Any]:
    audit = verify_log_integrity()
    timestamp = _now_utc().isoformat()
    return {
        "timestamp": timestamp,
        "head_hash": audit["head_hash"],
        "total_entries": audit["total_entries"],
        "note": note,
    }


def record_anchor(tx_ref: str, network: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    _ensure_dir()
    anchor = {
        "timestamp": _now_utc().isoformat(),
        "network": network,
        "tx_ref": tx_ref,
        "payload": payload or prepare_anchor_payload(),
    }
    with ANCHOR_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(anchor, ensure_ascii=False) + "\n")
    return anchor


def list_anchors(limit: int = 50) -> List[Dict[str, Any]]:
    _ensure_dir()
    if not ANCHOR_LOG.exists():
        return []
    rows = [json.loads(line) for line in ANCHOR_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    return rows[-max(1, limit) :]
