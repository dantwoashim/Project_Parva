#!/usr/bin/env python3
"""Snapshot current OpenAPI schemas for versioned contract freeze checks."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

OUT_PATHS = {
    "v3": PROJECT_ROOT / "docs" / "contracts" / "v3_openapi_snapshot.json",
    "v4": PROJECT_ROOT / "docs" / "contracts" / "v4_openapi_snapshot.json",
    "v5": PROJECT_ROOT / "docs" / "contracts" / "v5_openapi_snapshot.json",
}

PUBLIC_CONTRACT_ENV = {
    "PARVA_ROUTE_PROFILE": "public_reference",
    "PARVA_ENABLE_EXPERIMENTAL_API": "false",
    "PARVA_SHOW_PRIVATE_SCHEMA": "false",
    "PARVA_ENV": "public",
    "PARVA_SOURCE_URL": "https://github.com/dantwoashim/Project_Parva",
    "PARVA_PROVENANCE_ATTESTATION_KEY": "test-provenance-key",
    "PARVA_REQUIRE_PRECOMPUTED": "false",
    "PARVA_SERVE_FRONTEND": "false",
    "PARVA_RATE_LIMIT_ENABLED": "false",
}


def _schema_for_prefix(prefix: str) -> dict:
    old_values = {key: os.environ.get(key) for key in PUBLIC_CONTRACT_ENV}
    os.environ.update(PUBLIC_CONTRACT_ENV)
    try:
        from app.bootstrap.app_factory import create_app

        payload = create_app().openapi()
    finally:
        for key, old_value in old_values.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value
    schema = dict(payload)
    schema["paths"] = {
        path: spec for path, spec in payload.get("paths", {}).items() if path.startswith(prefix)
    }
    return schema


def main() -> int:
    parser = argparse.ArgumentParser(description="Snapshot current OpenAPI schemas")
    parser.add_argument("--track", choices=["v3", "v4", "v5", "all"], default="all")
    args = parser.parse_args()

    tracks = list(OUT_PATHS) if args.track == "all" else [args.track]
    generated_at = datetime.now(timezone.utc).isoformat()
    for track in tracks:
        path = OUT_PATHS[track]
        path.parent.mkdir(parents=True, exist_ok=True)
        schema = _schema_for_prefix(f"/{track}/")
        wrapper = {
            "generated_at": generated_at,
            "track": track,
            "route_profile": "public_reference",
            "schema": schema,
        }
        path.write_text(json.dumps(wrapper, indent=2), encoding="utf-8")
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
