#!/usr/bin/env python3
"""Generate OpenAPI artifacts for public route profiles."""

from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(os.getenv("PARVA_OPENAPI_PROFILE_DIR", PROJECT_ROOT / "docs" / "api-docs")).resolve()
PROFILES = ("public_reference", "developer_preview", "enterprise_preview")
PUBLIC_PROFILES = {"public_reference", "developer_preview"}


def _base_env(profile: str) -> dict[str, str]:
    return {
        "PARVA_ROUTE_PROFILE": profile,
        "PARVA_ENABLE_EXPERIMENTAL_API": "false",
        "PARVA_SHOW_PRIVATE_SCHEMA": "false",
        "PARVA_ENV": "public" if profile in PUBLIC_PROFILES else "test",
        "PARVA_SOURCE_URL": "https://github.com/dantwoashim/Project_Parva",
        "PARVA_REQUIRE_PRECOMPUTED": "false",
        "PARVA_SERVE_FRONTEND": "false",
        "PARVA_RATE_LIMIT_ENABLED": "false",
    }


def _install_env(values: dict[str, str]) -> dict[str, str | None]:
    old_values = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    return old_values


def _restore_env(old_values: dict[str, str | None]) -> None:
    for key, old_value in old_values.items():
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value


def _write_profile(profile: str) -> tuple[Path, int]:
    old_env = _install_env(_base_env(profile))
    try:
        from app.bootstrap.app_factory import create_app

        app = create_app()
        schema = app.openapi()
    finally:
        _restore_env(old_env)

    schema["x-parva-route-profile"] = profile
    schema["x-parva-experimental-api"] = False
    schema["x-parva-private-schema"] = False
    output = OUTPUT_DIR / f"openapi.{profile.replace('_', '-')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output, len(schema.get("paths", {}))


def main() -> int:
    for profile in PROFILES:
        output, path_count = _write_profile(profile)
        try:
            rendered = output.relative_to(PROJECT_ROOT)
        except ValueError:
            rendered = output
        print(f"Wrote {rendered} with {path_count} paths.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
