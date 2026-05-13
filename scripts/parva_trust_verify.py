#!/usr/bin/env python3
"""Verify Project Parva public trust artifacts from a fresh clone."""

# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.trust_infrastructure_service import (  # noqa: E402
    DEFAULT_TRUST_LOG_PATH,
    TrustInfrastructureError,
    canonical_json,
    sha256_text,
    validate_public_trust_artifacts,
)

from tools.release.verify_release import verify_release  # noqa: E402
from tools.trust.common import DEFAULT_MANIFEST_PATH, DEFAULT_SIGNATURE_PATH  # noqa: E402
from tools.trust.verify_log import verify_log  # noqa: E402
from tools.trust.verify_release_signature import verify_release_signature  # noqa: E402


def verify_chain_log() -> dict[str, object]:
    if not DEFAULT_TRUST_LOG_PATH.exists():
        raise TrustInfrastructureError(f"missing trust log: {DEFAULT_TRUST_LOG_PATH}")
    entries = []
    previous_hash = None
    with DEFAULT_TRUST_LOG_PATH.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            raw = line.strip()
            if not raw:
                continue
            row = json.loads(raw)
            expected_previous = row.get("previous_entry_hash")
            if expected_previous != previous_hash:
                raise TrustInfrastructureError(
                    f"trust log line {line_number}: previous_entry_hash mismatch"
                )
            entry_hash = row.get("entry_hash")
            body = dict(row)
            body.pop("entry_hash", None)
            expected_hash = "sha256:" + sha256_text(canonical_json(body))
            if entry_hash != expected_hash:
                raise TrustInfrastructureError(f"trust log line {line_number}: entry_hash mismatch")
            previous_hash = expected_hash
            entries.append(row)
    if not entries:
        raise TrustInfrastructureError("trust log is empty")
    return {
        "ok": True,
        "entries": len(entries),
        "last_entry_hash": previous_hash,
        "path": str(DEFAULT_TRUST_LOG_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }


def main() -> int:
    try:
        release_messages = verify_release(DEFAULT_MANIFEST_PATH)
        signature_messages = verify_release_signature(DEFAULT_MANIFEST_PATH, DEFAULT_SIGNATURE_PATH)
        transparency = verify_log()
        chain = verify_chain_log()
        trust = validate_public_trust_artifacts()
        if not trust["ok"]:
            raise TrustInfrastructureError("; ".join(trust["issues"]))
    except Exception as exc:  # noqa: BLE001
        print(f"Project Parva trust verification failed: {exc}", file=sys.stderr)
        return 1

    print("Project Parva trust verification")
    print(
        json.dumps(
            {
                "ok": True,
                "release_checks": len(release_messages),
                "signature_checks": len(signature_messages),
                "transparency_log": transparency,
                "chain_log": chain,
                "public_trust": trust,
            },
            indent=2,
            sort_keys=True,
        )
    )
    print("trust verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
