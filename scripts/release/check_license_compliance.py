#!/usr/bin/env python3
"""Validate first-party licensing metadata for the AGPL deployment path."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_LICENSE = "AGPL-3.0-or-later"


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _project_license(path: Path) -> str | None:
    payload = _load_toml(path)
    project = payload.get("project", {})
    license_value = project.get("license")
    if isinstance(license_value, dict):
        return license_value.get("text")
    if isinstance(license_value, str):
        return license_value
    return None


def _package_license(path: Path) -> str | None:
    payload = _load_json(path)
    license_value = payload.get("license")
    return license_value if isinstance(license_value, str) else None


def _lockfile_root_license(path: Path) -> str | None:
    payload = _load_json(path)
    packages = payload.get("packages", {})
    root_package = packages.get("", {})
    license_value = root_package.get("license")
    return license_value if isinstance(license_value, str) else None


def _require_text(path: Path, snippet: str, errors: list[str]) -> None:
    content = path.read_text(encoding="utf-8")
    if snippet not in content:
        errors.append(f"{path.relative_to(PROJECT_ROOT)} must mention: {snippet}")


def main() -> int:
    errors: list[str] = []

    root_pyproject = PROJECT_ROOT / "pyproject.toml"
    sdk_pyproject = PROJECT_ROOT / "sdk" / "python" / "pyproject.toml"
    frontend_package = PROJECT_ROOT / "frontend" / "package.json"
    frontend_lock = PROJECT_ROOT / "frontend" / "package-lock.json"
    license_file = PROJECT_ROOT / "LICENSE"
    readme = PROJECT_ROOT / "README.md"
    deployment_doc = PROJECT_ROOT / "docs" / "DEPLOYMENT.md"
    known_limits_doc = PROJECT_ROOT / "docs" / "KNOWN_LIMITS.md"
    third_party_doc = PROJECT_ROOT / "THIRD_PARTY_NOTICES.md"

    for label, path, actual in (
        ("root pyproject", root_pyproject, _project_license(root_pyproject)),
        ("sdk pyproject", sdk_pyproject, _project_license(sdk_pyproject)),
        ("frontend package.json", frontend_package, _package_license(frontend_package)),
        ("frontend package-lock.json", frontend_lock, _lockfile_root_license(frontend_lock)),
    ):
        if actual != EXPECTED_LICENSE:
            errors.append(f"{label} must declare {EXPECTED_LICENSE}, found {actual!r}")

    if "GNU AFFERO GENERAL PUBLIC LICENSE" not in license_file.read_text(encoding="utf-8"):
        errors.append("LICENSE must contain the GNU Affero General Public License text.")

    root_dependencies = _load_toml(root_pyproject).get("project", {}).get("dependencies", [])
    if any(str(dep).startswith("pyswisseph") for dep in root_dependencies):
        root_license = _project_license(root_pyproject) or ""
        if not root_license.lower().startswith("agpl-3.0"):
            errors.append("pyswisseph is present, so the root project license must stay AGPL-compatible.")

    _require_text(readme, "AGPL", errors)
    _require_text(readme, "PARVA_SOURCE_URL", errors)
    _require_text(deployment_doc, "PARVA_SOURCE_URL", errors)
    _require_text(deployment_doc, "/source", errors)
    _require_text(known_limits_doc, "AGPL", errors)
    _require_text(third_party_doc, "Swiss Ephemeris", errors)
    _require_text(third_party_doc, "pyswisseph", errors)

    if errors:
        print("License compliance check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("License compliance check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
