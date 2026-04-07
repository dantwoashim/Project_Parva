"""Append-only transparency log for provenance snapshots and rule changes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.storage.file_stores import FileTransparencyLogStore

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
    attestation: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
            "attestation": self.attestation,
        }

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

def get_transparency_store() -> FileTransparencyLogStore:
    return FileTransparencyLogStore(
        transparency_dir=TRANSPARENCY_DIR,
        log_path=TRANSPARENCY_LOG,
        anchor_path=ANCHOR_LOG,
    )


def load_log_entries() -> List[Dict[str, Any]]:
    return get_transparency_store().load_entries()

def append_entry(event_type: str, payload: Dict[str, Any]) -> TransparencyEntry:
    row = get_transparency_store().append_entry(event_type, payload)
    return TransparencyEntry(
        entry_id=str(row["entry_id"]),
        timestamp=str(row["timestamp"]),
        event_type=str(row["event_type"]),
        payload=dict(row["payload"]),
        prev_hash=str(row["prev_hash"]),
        entry_hash=str(row["entry_hash"]),
        attestation=dict(row["attestation"]),
    )


def append_snapshot_event(
    snapshot_id: str, dataset_hash: str, rules_hash: str
) -> TransparencyEntry:
    return append_entry(
        "snapshot_created",
        {
            "snapshot_id": snapshot_id,
            "dataset_hash": dataset_hash,
            "rules_hash": rules_hash,
        },
    )


def verify_log_integrity() -> Dict[str, Any]:
    return get_transparency_store().verify_integrity()


def replay_state() -> Dict[str, Any]:
    return get_transparency_store().replay_state()


def prepare_anchor_payload(note: str = "") -> Dict[str, Any]:
    audit = verify_log_integrity()
    timestamp = _now_utc().isoformat()
    return {
        "timestamp": timestamp,
        "head_hash": audit["head_hash"],
        "total_entries": audit["total_entries"],
        "note": note,
    }


def record_anchor(
    tx_ref: str, network: str, payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return get_transparency_store().record_anchor(
        tx_ref,
        network,
        payload or prepare_anchor_payload(),
    )


def list_anchors(limit: int = 50) -> List[Dict[str, Any]]:
    return get_transparency_store().list_anchors(limit=limit)
