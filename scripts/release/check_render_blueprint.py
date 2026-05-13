#!/usr/bin/env python3
"""Validate the public-demo Render blueprint."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RENDER_BLUEPRINT = PROJECT_ROOT / "render.yaml"


def _parse_env_vars(text: str) -> dict[str, dict[str, str]]:
    envs: dict[str, dict[str, str]] = {}
    current_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- key:"):
            current_key = stripped.split(":", 1)[1].strip()
            envs[current_key] = {}
            continue
        if current_key is None or ":" not in stripped:
            continue
        field, value = stripped.split(":", 1)
        envs[current_key][field.strip()] = value.strip().strip('"')
    return envs


def main() -> int:
    if not RENDER_BLUEPRINT.exists():
        print("render.yaml is missing.")
        return 1

    envs = _parse_env_vars(RENDER_BLUEPRINT.read_text(encoding="utf-8"))
    failures: list[str] = []

    expected_values = {
        "PARVA_ROUTE_PROFILE": "developer_preview",
        "PARVA_ENABLE_EXPERIMENTAL_API": "false",
        "PARVA_ALLOW_EXPERIMENTAL_IN_PROD": "false",
        "PARVA_SHOW_PRIVATE_SCHEMA": "false",
        "PARVA_ENV": "public",
        "PARVA_SOURCE_URL": "https://github.com/dantwoashim/Project_Parva",
        "PARVA_RATE_LIMIT_ENABLED": "true",
        "PARVA_RATE_LIMIT_BACKEND": "memory",
        "PARVA_REQUIRE_PRECOMPUTED": "false",
        "PARVA_SERVE_FRONTEND": "false",
        "CORS_ALLOW_ORIGINS": (
            "https://prabinghimire1.com.np,"
            "https://www.prabinghimire1.com.np,"
            "https://project-parva.pages.dev,"
            "https://dantwoashim.github.io"
        ),
    }

    for key, expected in expected_values.items():
        actual = envs.get(key, {}).get("value")
        if actual != expected:
            failures.append(f"{key} should be {expected!r} in render.yaml (found {actual!r}).")

    text = RENDER_BLUEPRINT.read_text(encoding="utf-8")
    if "--port $PORT" not in text:
        failures.append("Render startCommand must bind uvicorn to $PORT.")
    if "PARVA_REDIS_URL" in envs:
        failures.append("Public-demo Render blueprint should not require Redis.")

    admin_token = envs.get("PARVA_ADMIN_TOKEN", {}).get("value", "")
    if admin_token:
        failures.append("PARVA_ADMIN_TOKEN must not be hard-coded in render.yaml.")

    api_keys = envs.get("PARVA_API_KEYS", {}).get("value", "")
    if "parva-dev-read-key" in api_keys:
        failures.append("PARVA_API_KEYS must not contain local development credentials.")

    if failures:
        for failure in failures:
            print(f"[render-blueprint] {failure}")
        return 1

    print("Render blueprint check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
