#!/usr/bin/env python3
"""Snapshot current OpenAPI schemas for versioned contract freeze checks."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


OUT_PATHS = {
    "v3": PROJECT_ROOT / "docs" / "contracts" / "v3_openapi_snapshot.json",
    "v4": PROJECT_ROOT / "docs" / "contracts" / "v4_openapi_snapshot.json",
    "v5": PROJECT_ROOT / "docs" / "contracts" / "v5_openapi_snapshot.json",
}


def _schema_for_prefix(prefix: str) -> dict:
    payload = app.openapi()
    schema = dict(payload)
    schema["paths"] = {
        path: spec for path, spec in payload.get("paths", {}).items() if path.startswith(prefix)
    }
    return schema


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    for track, path in OUT_PATHS.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        schema = _schema_for_prefix(f"/{track}/")
        wrapper = {
            "generated_at": generated_at,
            "track": track,
            "schema": schema,
        }
        path.write_text(json.dumps(wrapper, indent=2), encoding="utf-8")
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
