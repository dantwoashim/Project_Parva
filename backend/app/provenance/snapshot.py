"""
Snapshot and hashing utilities for provenance metadata.

This module tracks dataset/rule hashes and creates reproducible snapshot records.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.engine.ephemeris_config import get_ephemeris_config
from app.engine.manifest import (
    CANONICAL_ENGINE_ID,
    CANONICAL_MANIFEST_VERSION,
    build_engine_manifest,
)
from app.provenance.attestation import (
    attestation_key_configured,
    build_attestation,
    canonical_json,
    verify_attestation,
)
from app.storage.interfaces import SnapshotStore

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DATA_DIR = BACKEND_ROOT / "data"
SNAPSHOT_DIR = BACKEND_DATA_DIR / "snapshots"
ARTIFACT_DIR = SNAPSHOT_DIR / "artifacts"
LEGACY_FESTIVAL_SNAPSHOT = BACKEND_DATA_DIR / "snapshot.json"
PRECOMPUTED_DIR = PROJECT_ROOT / "output" / "precomputed"
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
DEFAULT_DEPENDENCY_LOCK_FILES = [
    PROJECT_ROOT / "pyproject.toml",
    PROJECT_ROOT / "requirements" / "constraints.txt",
    PROJECT_ROOT / "frontend" / "package-lock.json",
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
    manifest_version: str = CANONICAL_MANIFEST_VERSION
    canonical_engine_id: str = CANONICAL_ENGINE_ID
    manifest_hash: Optional[str] = None
    artifact_id: Optional[str] = None
    artifact_root: Optional[str] = None
    artifact_paths: dict[str, str] = field(default_factory=dict)
    build_sha: Optional[str] = None
    dependency_lock_hash: Optional[str] = None
    python_runtime: Optional[str] = None
    ephemeris_header: Optional[str] = None
    engine_manifest: dict[str, Any] = field(default_factory=dict)
    attestation: dict[str, Any] = field(default_factory=dict)

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
            "manifest_version": self.manifest_version,
            "canonical_engine_id": self.canonical_engine_id,
            "manifest_hash": self.manifest_hash,
            "artifact_id": self.artifact_id,
            "artifact_root": self.artifact_root,
            "artifact_paths": self.artifact_paths,
            "build_sha": self.build_sha,
            "dependency_lock_hash": self.dependency_lock_hash,
            "python_runtime": self.python_runtime,
            "ephemeris_header": self.ephemeris_header,
            "engine_manifest": self.engine_manifest,
            "attestation": self.attestation,
        }

    def signing_payload(self) -> dict[str, Any]:
        payload = self.to_dict()
        payload.pop("attestation", None)
        payload.pop("artifact_id", None)
        payload.pop("artifact_root", None)
        payload.pop("artifact_paths", None)
        return payload

    def manifest_payload(self) -> dict[str, Any]:
        payload = self.signing_payload()
        payload.pop("manifest_hash", None)
        return payload


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


def _display_path(path: Path) -> str:
    try:
        rel = path.relative_to(PROJECT_ROOT)
        return rel.as_posix()
    except ValueError:
        try:
            rel = path.resolve().relative_to(PROJECT_ROOT.resolve())
            return rel.as_posix()
        except ValueError:
            return path.name


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


def _artifact_root_path(manifest_hash: str) -> Path:
    return ARTIFACT_DIR / manifest_hash


def _dependency_lock_hash() -> str:
    return _hash_file_set(DEFAULT_DEPENDENCY_LOCK_FILES, {"type": "dependency-lock"})


def _build_sha() -> str | None:
    env_sha = os.getenv("PARVA_BUILD_SHA", "").strip()
    if env_sha:
        return env_sha
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


class FileSnapshotStore(SnapshotStore):
    def create(self, snapshot_id: Optional[str] = None) -> SnapshotRecord:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        now_utc = datetime.now(timezone.utc)
        sid = snapshot_id or _generate_snapshot_id(now_utc)

        dataset_hash = hash_dataset()
        rules_hash = hash_rules()

        dataset_files = [_display_path(p) for p in _existing_paths(DEFAULT_DATASET_FILES)]
        rule_files = [_display_path(p) for p in _existing_paths(DEFAULT_RULE_FILES)]

        festival_snapshot_copy: Optional[str] = None
        if LEGACY_FESTIVAL_SNAPSHOT.exists():
            copied = SNAPSHOT_DIR / f"{sid}.festival_snapshot.json"
            shutil.copyfile(LEGACY_FESTIVAL_SNAPSHOT, copied)
            festival_snapshot_copy = _display_path(copied)

        record = SnapshotRecord(
            snapshot_id=sid,
            created_at=now_utc.isoformat(),
            dataset_hash=dataset_hash,
            rules_hash=rules_hash,
            engine_version="v3",
            dataset_files=dataset_files,
            rule_files=rule_files,
            festival_snapshot_path=festival_snapshot_copy,
            manifest_version=CANONICAL_MANIFEST_VERSION,
            canonical_engine_id=CANONICAL_ENGINE_ID,
            build_sha=_build_sha(),
            dependency_lock_hash=_dependency_lock_hash(),
            python_runtime=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            ephemeris_header=get_ephemeris_config().header_value,
            engine_manifest=build_engine_manifest(),
        )
        record.manifest_hash = hashlib.sha256(
            canonical_json(record.manifest_payload()).encode("utf-8")
        ).hexdigest()
        record.artifact_id = f"sha256:{record.manifest_hash}"
        record.attestation = build_attestation(record.signing_payload())

        artifact_root = _artifact_root_path(record.manifest_hash)
        artifact_root.mkdir(parents=True, exist_ok=True)
        record.artifact_root = _display_path(artifact_root)
        record.artifact_paths = {
            "snapshot": _display_path(artifact_root / "snapshot.json"),
        }
        if LEGACY_FESTIVAL_SNAPSHOT.exists():
            artifact_festival_snapshot = artifact_root / "festival_snapshot.json"
            shutil.copyfile(LEGACY_FESTIVAL_SNAPSHOT, artifact_festival_snapshot)
            record.artifact_paths["festival_snapshot"] = _display_path(artifact_festival_snapshot)
        if PRECOMPUTED_DIR.exists():
            artifact_precomputed_dir = artifact_root / "precomputed"
            artifact_precomputed_dir.mkdir(parents=True, exist_ok=True)
            copied_files: list[str] = []
            for source in sorted(PRECOMPUTED_DIR.glob("*.json")):
                destination = artifact_precomputed_dir / source.name
                shutil.copyfile(source, destination)
                copied_files.append(_display_path(destination))
            if copied_files:
                manifest_path = artifact_precomputed_dir / "manifest.json"
                manifest_path.write_text(
                    json.dumps({"files": copied_files}, indent=2),
                    encoding="utf-8",
                )
                record.artifact_paths["precomputed_root"] = _display_path(artifact_precomputed_dir)
                record.artifact_paths["precomputed_manifest"] = _display_path(manifest_path)

        path = _snapshot_path(sid)
        path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
        (artifact_root / "snapshot.json").write_text(
            json.dumps(record.to_dict(), indent=2),
            encoding="utf-8",
        )
        LATEST_POINTER.write_text(json.dumps({"snapshot_id": sid}, indent=2), encoding="utf-8")
        return record

    def load(self, snapshot_id: str) -> SnapshotRecord:
        path = _snapshot_path(snapshot_id)
        if not path.exists():
            raise FileNotFoundError(f"Snapshot not found: {snapshot_id}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        return SnapshotRecord(**payload)

    def latest_id(self) -> Optional[str]:
        if LATEST_POINTER.exists():
            payload = json.loads(LATEST_POINTER.read_text(encoding="utf-8"))
            sid = payload.get("snapshot_id")
            if sid:
                return sid

        records = sorted(SNAPSHOT_DIR.glob("snap_*.json"), key=lambda p: p.stat().st_mtime)
        if not records:
            return None
        return records[-1].stem

    def latest(self, *, create_if_missing: bool = False) -> Optional[SnapshotRecord]:
        sid = self.latest_id()
        if sid:
            try:
                snapshot = self.load(sid)
                if create_if_missing and _snapshot_requires_refresh(snapshot):
                    return create_snapshot()
                return snapshot
            except Exception:
                sid = None
        if create_if_missing:
            return create_snapshot()
        return None

    def verify(self, snapshot_id: str) -> dict[str, Any]:
        record = self.load(snapshot_id)
        dataset_now = hash_dataset()
        rules_now = hash_rules()
        checks = {
            "dataset_hash_match": dataset_now == record.dataset_hash,
            "rules_hash_match": rules_now == record.rules_hash,
            "manifest_hash_match": hashlib.sha256(
                canonical_json(record.manifest_payload()).encode("utf-8")
            ).hexdigest()
            == record.manifest_hash,
            "attestation_valid": verify_attestation(record.signing_payload(), record.attestation),
        }
        valid = all(checks.values())
        return {
            "snapshot_id": snapshot_id,
            "valid": valid,
            "checks": checks,
            "expected": {
                "dataset_hash": record.dataset_hash,
                "rules_hash": record.rules_hash,
                "manifest_hash": record.manifest_hash,
            },
            "actual": {
                "dataset_hash": dataset_now,
                "rules_hash": rules_now,
                "manifest_hash": hashlib.sha256(
                    canonical_json(record.manifest_payload()).encode("utf-8")
                ).hexdigest(),
            },
        }

    def provenance_payload(
        self,
        *,
        verify_url: Optional[str] = None,
        create_if_missing: bool = True,
    ) -> dict[str, Any]:
        snapshot = self.latest(create_if_missing=create_if_missing)
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
            "canonical_engine_id": snapshot.canonical_engine_id,
            "manifest_version": snapshot.manifest_version,
            "manifest_hash": snapshot.manifest_hash,
            "artifact_id": snapshot.artifact_id,
            "artifact_root": snapshot.artifact_root,
            "artifact_paths": snapshot.artifact_paths,
            "attestation": snapshot.attestation,
            "verify_url": verify_url,
        }


def get_snapshot_store() -> FileSnapshotStore:
    return FileSnapshotStore()


def create_snapshot(snapshot_id: Optional[str] = None) -> SnapshotRecord:
    return get_snapshot_store().create(snapshot_id)


def load_snapshot(snapshot_id: str) -> SnapshotRecord:
    return get_snapshot_store().load(snapshot_id)


def get_latest_snapshot_id() -> Optional[str]:
    return get_snapshot_store().latest_id()


def get_latest_snapshot(create_if_missing: bool = False) -> Optional[SnapshotRecord]:
    return get_snapshot_store().latest(create_if_missing=create_if_missing)


def _snapshot_requires_refresh(record: SnapshotRecord) -> bool:
    if record.manifest_version != CANONICAL_MANIFEST_VERSION:
        return True
    if record.canonical_engine_id != CANONICAL_ENGINE_ID:
        return True
    if not record.manifest_hash:
        return True
    attestation_mode = str((record.attestation or {}).get("mode") or "")
    if not attestation_mode:
        return True
    if not verify_attestation(record.signing_payload(), record.attestation):
        return True
    if attestation_mode == "unsigned" and attestation_key_configured():
        return True
    return False


def verify_snapshot(snapshot_id: str) -> dict[str, Any]:
    return get_snapshot_store().verify(snapshot_id)


def get_provenance_payload(
    *,
    verify_url: Optional[str] = None,
    create_if_missing: bool = True,
) -> dict[str, Any]:
    return get_snapshot_store().provenance_payload(
        verify_url=verify_url,
        create_if_missing=create_if_missing,
    )
