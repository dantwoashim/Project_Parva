#!/usr/bin/env python3
"""Validate the zero-budget Render blueprint against current production expectations."""

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
        "PARVA_ENABLE_EXPERIMENTAL_API": "false",
        "PARVA_ALLOW_EXPERIMENTAL_IN_PROD": "false",
        "PARVA_ENV": "production",
        "PARVA_RATE_LIMIT_ENABLED": "true",
        "PARVA_SERVE_FRONTEND": "true",
    }

    for key, expected in expected_values.items():
        actual = envs.get(key, {}).get("value")
        if actual != expected:
            failures.append(f"{key} should be {expected!r} in render.yaml (found {actual!r}).")

    source_url = envs.get("PARVA_SOURCE_URL")
    if not source_url:
        failures.append("PARVA_SOURCE_URL is missing from render.yaml.")
    else:
        source_value = source_url.get("value", "")
        source_sync = source_url.get("sync", "")
        if not source_value and source_sync.lower() != "false":
            failures.append(
                "PARVA_SOURCE_URL must either define a value or use sync: false for operator-supplied configuration."
            )

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
