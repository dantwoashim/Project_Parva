#!/usr/bin/env python3
"""Check current OpenAPI against frozen versioned snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


DEFAULT_SNAPSHOTS = {
    "v3": PROJECT_ROOT / "docs" / "contracts" / "v3_openapi_snapshot.json",
    "v4": PROJECT_ROOT / "docs" / "contracts" / "v4_openapi_snapshot.json",
    "v5": PROJECT_ROOT / "docs" / "contracts" / "v5_openapi_snapshot.json",
}


def _normalize(schema: dict) -> dict:
    # Ignore volatile metadata.
    schema = dict(schema)
    info = dict(schema.get("info", {}))
    if "version" in info:
        info["version"] = "<frozen>"
    schema["info"] = info
    return schema


def _schema_for_prefix(prefix: str) -> dict:
    payload = app.openapi()
    schema = dict(payload)
    schema["paths"] = {
        path: spec for path, spec in payload.get("paths", {}).items() if path.startswith(prefix)
    }
    return schema


def _check_track(track: str, snapshot_path: Path) -> int:
    if not snapshot_path.exists():
        print(f"[{track}] Missing snapshot: {snapshot_path}")
        return 2

    snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    frozen = _normalize(snapshot_payload.get("schema", {}))
    current = _normalize(_schema_for_prefix(f"/{track}/"))

    if frozen == current:
        print(f"[{track}] Contract freeze check passed.")
        return 0

    print(f"[{track}] Contract freeze check failed: schema differs from snapshot.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenAPI freeze checker")
    parser.add_argument("--track", choices=["v3", "v4", "v5", "all"], default="all")
    parser.add_argument("--snapshot", help="Optional custom snapshot path for single-track checks")
    args = parser.parse_args()

    if args.snapshot:
        if args.track == "all":
            print("--snapshot requires --track v3, --track v4, or --track v5")
            return 2
        return _check_track(args.track, Path(args.snapshot))

    tracks = ["v3", "v4", "v5"] if args.track == "all" else [args.track]
    codes = [_check_track(track, DEFAULT_SNAPSHOTS[track]) for track in tracks]
    if 2 in codes:
        return 2
    if 1 in codes:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
