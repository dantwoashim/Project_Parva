#!/usr/bin/env python3
"""Fail when the static public OpenAPI mirror is stale."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from scripts.release.openapi_normalization import normalized_openapi_json
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from openapi_normalization import normalized_openapi_json

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_OPENAPI = PROJECT_ROOT / "docs" / "api-docs" / "openapi.json"


def main() -> int:
    if not STATIC_OPENAPI.exists():
        print(f"Static OpenAPI mirror is missing: {STATIC_OPENAPI}")
        return 1

    with tempfile.TemporaryDirectory(prefix="parva-openapi-") as tmp:
        generated = Path(tmp) / "openapi.json"
        env = os.environ.copy()
        env["PARVA_OPENAPI_OUTPUT"] = str(generated)
        env.setdefault("PARVA_ROUTE_PROFILE", "developer_preview")
        env.setdefault("PARVA_ENABLE_EXPERIMENTAL_API", "false")
        env.setdefault("PARVA_SHOW_PRIVATE_SCHEMA", "false")
        env.setdefault("PARVA_ENV", "public")
        env.setdefault("PARVA_SOURCE_URL", "https://github.com/dantwoashim/Project_Parva")
        env.setdefault("PARVA_REQUIRE_PRECOMPUTED", "false")
        env.setdefault("PARVA_RATE_LIMIT_ENABLED", "false")
        result = subprocess.run(
            [sys.executable, "scripts/release/generate_public_demo_openapi.py"],
            cwd=PROJECT_ROOT,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode

        if normalized_openapi_json(generated) != normalized_openapi_json(STATIC_OPENAPI):
            print(
                "Static public OpenAPI mirror is stale. "
                "Run: python scripts/release/generate_public_demo_openapi.py"
            )
            return 1

    print("Static public OpenAPI mirror is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
