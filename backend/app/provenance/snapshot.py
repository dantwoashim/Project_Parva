"""
Snapshot and hashing utilities for provenance metadata.

This module tracks dataset/rule hashes and creates reproducible snapshot records.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.engine.ephemeris_config import get_ephemeris_config


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DATA_DIR = BACKEND_ROOT / "data"
SNAPSHOT_DIR = BACKEND_DATA_DIR / "snapshots"
LEGACY_FESTIVAL_SNAPSHOT = BACKEND_DATA_DIR / "snapshot.json"
LATEST_POINTER = SNAPSHOT_DIR / "latest.json"


DEFAULT_DATASET_FILES = [
    PROJECT_ROOT / "data" / "festivals" / "festivals.json",
    PROJECT_ROOT / "data" / "normalized_sources.json",
    PROJECT_ROOT / "data" / "ground_truth" / "discrepancies.json",
    BACKEND_ROOT / "app" / "calendar" / "sources.json",
    BACKEND_ROOT / "app" / "calendar" / "ground_truth_overrides.json",
    LEGACY_FESTIVAL_SNAPSHOT,
]

DEFAULT_RULE_FILES = [
    BACKEND_ROOT / "app" / "calendar" / "festival_rules_v3.json",
    BACKEND_ROOT / "app" / "calendar" / "festival_rules.json",
]


@dataclass
class SnapshotRecord:
    """Typed snapshot record."""

    snapshot_id: str
    created_at: str
    dataset_hash: str
    rules_hash: str
    engine_version: str
    dataset_files: list[str]
    rule_files: list[str]
    festival_snapshot_path: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "created_at": self.created_at,
            "dataset_hash": self.dataset_hash,
            "rules_hash": self.rules_hash,
            "engine_version": self.engine_version,
            "dataset_files": self.dataset_files,
            "rule_files": self.rule_files,
            "festival_snapshot_path": self.festival_snapshot_path,
        }


def _canonical_json_bytes(path: Path) -> bytes:
    data = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return canonical.encode("utf-8")


def _file_digest(path: Path) -> str:
    if path.suffix.lower() == ".json":
        payload = _canonical_json_bytes(path)
    else:
        payload = path.read_bytes()
    return hashlib.sha256(payload).hexdigest()


def _existing_paths(paths: list[Path]) -> list[Path]:
    return sorted([p for p in paths if p.exists()], key=lambda p: str(p))


def _hash_file_set(paths: list[Path], context: dict[str, Any]) -> str:
    h = hashlib.sha256()
    h.update(json.dumps(context, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    for path in _existing_paths(paths):
        rel = path.relative_to(PROJECT_ROOT) if path.is_relative_to(PROJECT_ROOT) else path
        h.update(str(rel).encode("utf-8"))
        h.update(_file_digest(path).encode("utf-8"))
    return h.hexdigest()


def hash_dataset(dataset_files: Optional[list[Path]] = None) -> str:
    """Hash canonical dataset files deterministically."""
    files = dataset_files or DEFAULT_DATASET_FILES
    return _hash_file_set(files, {"type": "dataset"})


def hash_rules(
    rule_files: Optional[list[Path]] = None,
    engine_config: Optional[dict[str, Any]] = None,
) -> str:
    """Hash rule files plus ephemeris engine settings."""
    files = rule_files or DEFAULT_RULE_FILES
    cfg = engine_config
    if cfg is None:
        runtime = get_ephemeris_config()
        cfg = {
            "ephemeris_mode": runtime.ephemeris_mode,
            "ayanamsa": runtime.ayanamsa,
            "coordinate_system": runtime.coordinate_system,
            "header_value": runtime.header_value,
        }
    return _hash_file_set(files, {"type": "rules", "engine_config": cfg})


def _generate_snapshot_id(now_utc: datetime) -> str:
    return f"snap_{now_utc.strftime('%Y%m%dT%H%M%SZ')}"


def _snapshot_path(snapshot_id: str) -> Path:
    return SNAPSHOT_DIR / f"{snapshot_id}.json"


def create_snapshot(snapshot_id: Optional[str] = None) -> SnapshotRecord:
    """
    Create a snapshot record under backend/data/snapshots.

    Also persists latest pointer and a copy of the festival snapshot used for proofs.
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    now_utc = datetime.now(timezone.utc)
    sid = snapshot_id or _generate_snapshot_id(now_utc)

    dataset_hash = hash_dataset()
    rules_hash = hash_rules()

    dataset_files = [str(p) for p in _existing_paths(DEFAULT_DATASET_FILES)]
    rule_files = [str(p) for p in _existing_paths(DEFAULT_RULE_FILES)]

    festival_snapshot_copy: Optional[str] = None
    if LEGACY_FESTIVAL_SNAPSHOT.exists():
        copied = SNAPSHOT_DIR / f"{sid}.festival_snapshot.json"
        shutil.copyfile(LEGACY_FESTIVAL_SNAPSHOT, copied)
        festival_snapshot_copy = str(copied)

    record = SnapshotRecord(
        snapshot_id=sid,
        created_at=now_utc.isoformat(),
        dataset_hash=dataset_hash,
        rules_hash=rules_hash,
        engine_version="v2",
        dataset_files=dataset_files,
        rule_files=rule_files,
        festival_snapshot_path=festival_snapshot_copy,
    )

    path = _snapshot_path(sid)
    path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
    LATEST_POINTER.write_text(json.dumps({"snapshot_id": sid}, indent=2), encoding="utf-8")
    return record


def load_snapshot(snapshot_id: str) -> SnapshotRecord:
    """Load a snapshot record by id."""
    path = _snapshot_path(snapshot_id)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SnapshotRecord(**payload)


def get_latest_snapshot_id() -> Optional[str]:
    """Get latest snapshot id from pointer or by file mtime fallback."""
    if LATEST_POINTER.exists():
        payload = json.loads(LATEST_POINTER.read_text(encoding="utf-8"))
        sid = payload.get("snapshot_id")
        if sid:
            return sid

    records = sorted(SNAPSHOT_DIR.glob("snap_*.json"), key=lambda p: p.stat().st_mtime)
    if not records:
        return None
    return records[-1].stem


def get_latest_snapshot(create_if_missing: bool = False) -> Optional[SnapshotRecord]:
    sid = get_latest_snapshot_id()
    if sid:
        try:
            return load_snapshot(sid)
        except Exception:
            pass
    if create_if_missing:
        return create_snapshot()
    return None


def verify_snapshot(snapshot_id: str) -> dict[str, Any]:
    """Recompute hashes and verify integrity of stored snapshot record."""
    record = load_snapshot(snapshot_id)
    dataset_now = hash_dataset()
    rules_now = hash_rules()

    checks = {
        "dataset_hash_match": dataset_now == record.dataset_hash,
        "rules_hash_match": rules_now == record.rules_hash,
    }
    valid = all(checks.values())
    return {
        "snapshot_id": snapshot_id,
        "valid": valid,
        "checks": checks,
        "expected": {
            "dataset_hash": record.dataset_hash,
            "rules_hash": record.rules_hash,
        },
        "actual": {
            "dataset_hash": dataset_now,
            "rules_hash": rules_now,
        },
    }


def get_provenance_payload(
    *,
    verify_url: Optional[str] = None,
    create_if_missing: bool = True,
) -> dict[str, Any]:
    """
    Build a provenance object for API responses.
    """
    snapshot = get_latest_snapshot(create_if_missing=create_if_missing)
    if not snapshot:
        return {
            "dataset_hash": None,
            "rules_hash": None,
            "snapshot_id": None,
            "verify_url": verify_url,
        }
    return {
        "dataset_hash": snapshot.dataset_hash,
        "rules_hash": snapshot.rules_hash,
        "snapshot_id": snapshot.snapshot_id,
        "verify_url": verify_url,
    }
