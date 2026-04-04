#!/usr/bin/env python3
"""Validate that release provenance metadata is complete and verifiable."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.provenance.attestation import canonical_json, verify_attestation
from app.provenance.snapshot import LATEST_POINTER, SNAPSHOT_DIR, create_snapshot


def _remove_if_exists(path: Path | None) -> None:
    if path and path.exists():
        path.unlink()


def _restore_latest_pointer(previous_payload: str | None, temp_snapshot_id: str) -> None:
    if previous_payload is not None:
        LATEST_POINTER.write_text(previous_payload, encoding="utf-8")
        return

    if not LATEST_POINTER.exists():
        return

    try:
        payload = json.loads(LATEST_POINTER.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    if payload.get("snapshot_id") == temp_snapshot_id:
        LATEST_POINTER.unlink()


def _validate_record(record, require_signed: bool) -> list[str]:
    failures: list[str] = []

    required_fields = {
        "snapshot_id": record.snapshot_id,
        "created_at": record.created_at,
        "dataset_hash": record.dataset_hash,
        "rules_hash": record.rules_hash,
        "manifest_version": record.manifest_version,
        "canonical_engine_id": record.canonical_engine_id,
        "manifest_hash": record.manifest_hash,
        "dependency_lock_hash": record.dependency_lock_hash,
        "python_runtime": record.python_runtime,
        "ephemeris_header": record.ephemeris_header,
    }
    missing = sorted([name for name, value in required_fields.items() if not value])
    if missing:
        failures.append(f"Missing required provenance fields: {', '.join(missing)}")

    if (PROJECT_ROOT / ".git").exists() and not record.build_sha:
        failures.append("Expected build_sha for a git checkout, but the snapshot record did not include one.")

    if record.engine_manifest.get("canonical_engine_id") != record.canonical_engine_id:
        failures.append("Engine manifest canonical_engine_id does not match the snapshot record.")

    route_families = record.engine_manifest.get("public_route_families")
    if not isinstance(route_families, list) or not route_families:
        failures.append("Engine manifest is missing public_route_families.")

    expected_manifest_hash = hashlib.sha256(
        canonical_json(record.manifest_payload()).encode("utf-8")
    ).hexdigest()
    if record.manifest_hash != expected_manifest_hash:
        failures.append("manifest_hash does not match the canonical manifest payload.")

    if require_signed and record.attestation.get("mode") == "unsigned":
        failures.append(
            "Release provenance must be signed. Set PARVA_PROVENANCE_ATTESTATION_KEY for release candidate runs."
        )

    if not verify_attestation(record.signing_payload(), record.attestation):
        failures.append("Attestation verification failed for the generated snapshot payload.")

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-signed",
        action="store_true",
        help="Fail if the generated provenance attestation is unsigned.",
    )
    parser.add_argument(
        "--keep-check-artifacts",
        action="store_true",
        help="Keep the temporary snapshot files generated during validation.",
    )
    args = parser.parse_args(argv)

    previous_pointer_payload = (
        LATEST_POINTER.read_text(encoding="utf-8") if LATEST_POINTER.exists() else None
    )
    temp_snapshot_id = "provcheck_release_candidate"
    snapshot_path = SNAPSHOT_DIR / f"{temp_snapshot_id}.json"
    snapshot_copy_path = SNAPSHOT_DIR / f"{temp_snapshot_id}.festival_snapshot.json"

    record = create_snapshot(snapshot_id=temp_snapshot_id)
    failures = _validate_record(record, require_signed=args.require_signed)

    if not args.keep_check_artifacts:
        _remove_if_exists(snapshot_path)
        _remove_if_exists(snapshot_copy_path)
        _restore_latest_pointer(previous_pointer_payload, temp_snapshot_id)

    if failures:
        for failure in failures:
            print(f"[provenance] {failure}")
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "snapshot_id": record.snapshot_id,
                "attestation_mode": record.attestation.get("mode"),
                "manifest_version": record.manifest_version,
                "canonical_engine_id": record.canonical_engine_id,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
