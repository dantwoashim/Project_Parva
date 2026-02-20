#!/usr/bin/env python3
"""Check current OpenAPI against frozen snapshots.

Default behavior validates only v3 public profile.
Pass --track v4 or --track v5 for experimental checks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


SNAPSHOTS = {
    "v3": PROJECT_ROOT / "docs" / "contracts" / "v3_openapi_snapshot.json",
    "v4": PROJECT_ROOT / "docs" / "contracts" / "v4_openapi_snapshot.json",
    "v5": PROJECT_ROOT / "docs" / "contracts" / "v5_openapi_snapshot.json",
}


def _normalize(schema: dict) -> dict:
    schema = dict(schema)
    info = dict(schema.get("info", {}))
    if "version" in info:
        info["version"] = "<frozen>"
    schema["info"] = info

    components = dict(schema.get("components", {}))
    schemas = dict(components.get("schemas", {}))
    validation_error = dict(schemas.get("ValidationError", {}))
    properties = dict(validation_error.get("properties", {}))

    for volatile_key in ("input", "ctx"):
        properties.pop(volatile_key, None)

    if properties:
        validation_error["properties"] = properties
    required = validation_error.get("required")
    if isinstance(required, list):
        validation_error["required"] = [k for k in required if k not in {"input", "ctx"}]
    if validation_error:
        schemas["ValidationError"] = validation_error
    if schemas:
        components["schemas"] = schemas
    if components:
        schema["components"] = components

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


def _default_tracks() -> list[str]:
    # Public-profile CI only enforces v3 unless explicitly requested.
    if os.getenv("PARVA_ENABLE_EXPERIMENTAL_API", "").strip().lower() in {"1", "true", "yes", "on"}:
        return ["v3", "v4", "v5"]
    return ["v3"]


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

    tracks = _default_tracks() if args.track == "all" else [args.track]
    codes = [_check_track(track, SNAPSHOTS[track]) for track in tracks]
    if 2 in codes:
        return 2
    if 1 in codes:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
