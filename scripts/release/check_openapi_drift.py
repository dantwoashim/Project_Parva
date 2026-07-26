#!/usr/bin/env python3
"""Fail when public OpenAPI artifacts are stale or expose private research routes."""

from __future__ import annotations

import json
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
PROFILE_SPECS = {
    "public_reference": PROJECT_ROOT / "docs" / "api-docs" / "openapi.public-reference.json",
    "developer_preview": PROJECT_ROOT / "docs" / "api-docs" / "openapi.developer-preview.json",
    "enterprise_preview": PROJECT_ROOT / "docs" / "api-docs" / "openapi.enterprise-preview.json",
}
PRIVATE_PREFIXES = ("/v4/api/future-bs/", "/v5/api/calendar-model-risk/")
SAFE_CAPABILITY_PATHS = {
    "/v4/api/future-bs/capabilities",
    "/v5/api/calendar-model-risk/capabilities",
}


def _run(command: list[str], env: dict[str, str] | None = None) -> int:
    result = subprocess.run(command, cwd=PROJECT_ROOT, env=env, check=False)
    return result.returncode


def _check_private_paths(path: Path, *, label: str) -> list[str]:
    failures: list[str] = []
    spec = json.loads(path.read_text(encoding="utf-8"))
    for api_path in spec.get("paths", {}):
        if any(api_path.startswith(prefix) for prefix in PRIVATE_PREFIXES) and api_path not in SAFE_CAPABILITY_PATHS:
            failures.append(f"{label} exposes private/research path: {api_path}")
    return failures


def main() -> int:
    public_drift = _run([sys.executable, "scripts/release/check_public_openapi_drift.py"])
    if public_drift != 0:
        return public_drift

    for profile, path in PROFILE_SPECS.items():
        if not path.exists():
            print(f"Missing checked-in profile OpenAPI spec for {profile}: {path}")
            return 1

    with tempfile.TemporaryDirectory(prefix="parva-profile-openapi-") as tmp:
        env = os.environ.copy()
        env["PARVA_OPENAPI_PROFILE_DIR"] = tmp
        generated_result = _run([sys.executable, "scripts/release/generate_openapi_profiles.py"], env=env)
        if generated_result != 0:
            return generated_result

        failures: list[str] = []
        for profile, checked_in in PROFILE_SPECS.items():
            generated = Path(tmp) / checked_in.name
            if not generated.exists():
                failures.append(f"Generator did not produce {generated.name} for {profile}.")
                continue
            if normalized_openapi_json(generated) != normalized_openapi_json(checked_in):
                failures.append(
                    f"Profile OpenAPI spec is stale for {profile}. "
                    "Run: python scripts/release/generate_openapi_profiles.py"
                )
            failures.extend(_check_private_paths(checked_in, label=profile))

    if failures:
        print("\n".join(failures))
        return 1

    print("Static public and profile OpenAPI artifacts are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
