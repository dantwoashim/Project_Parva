#!/usr/bin/env python3
"""Validate checked-in source dockets and extraction receipts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.sources.docket import SourceDocket  # noqa: E402
from app.sources.hashing import sha256_file  # noqa: E402


def main() -> int:
    docket_dir = PROJECT_ROOT / "data" / "sources" / "dockets"
    failures: list[str] = []
    for path in sorted(docket_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        docket = SourceDocket.from_dict(payload)
        for artifact in (docket.raw_artifact, docket.normalized_output):
            artifact_path = PROJECT_ROOT / artifact.path
            if not artifact_path.exists():
                failures.append(f"{path}: missing artifact {artifact.path}")
                continue
            if sha256_file(artifact_path) != artifact.sha256:
                failures.append(f"{path}: hash mismatch for {artifact.path}")
    if failures:
        print("\n".join(failures))
        return 1
    print("Source dockets validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
