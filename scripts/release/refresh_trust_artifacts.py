#!/usr/bin/env python3
"""Refresh public trust artifacts in one deterministic pass.

This script keeps the immutable snapshot-addressed provenance record and the
public trust artifacts in sync so release/ops workflows have one entry point.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.provenance.snapshot import create_snapshot  # noqa: E402


def _run(script: Path, *, optional: bool = False, reason: str | None = None) -> None:
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=PROJECT_ROOT,
        check=not optional,
        capture_output=True,
        text=True,
    )
    if optional and completed.returncode != 0:
        message = reason or f"Skipping optional step {script.name}"
        print(f"{message}: {completed.stderr.strip() or completed.stdout.strip()}")
        return
    if completed.stdout.strip():
        print(completed.stdout.strip())


def main() -> int:
    snapshot = create_snapshot()
    print(
        json.dumps(
            {
                "snapshot_id": snapshot.snapshot_id,
                "artifact_id": snapshot.artifact_id,
                "artifact_root": snapshot.artifact_root,
            },
            indent=2,
        )
    )

    _run(PROJECT_ROOT / "backend" / "tools" / "build_source_review_queue.py")
    _run(PROJECT_ROOT / "backend" / "tools" / "build_boundary_suite.py")
    _run(
        PROJECT_ROOT / "scripts" / "generate_authority_dashboard.py",
        optional=True,
        reason="Skipping authority dashboard refresh until release report inputs exist",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
