#!/usr/bin/env python3
"""Check public package metadata before registry dry-runs or publication."""

from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_PACKAGES = (
    ROOT / "packages" / "parva-python",
    ROOT / "packages" / "parva-ai-tools",
    ROOT / "packages" / "parva-mcp-server",
)
NPM_PACKAGES = (ROOT / "packages" / "parva-js", ROOT / "packages" / "parva-local-kernel")
FORBIDDEN_FILE_PARTS = (
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    ".env",
    ".pem",
    ".key",
    "private",
)
UNSAFE_CLAIMS = (
    "government approved",
    "official future bs",
    "guaranteed future",
    "panchanga replacement",
    "soc 2",
)


def _git_files(package_dir: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--", str(package_dir.relative_to(ROOT)).replace("\\", "/")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _read_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_readme(package_dir: Path, issues: list[str]) -> None:
    readme = package_dir / "README.md"
    if not readme.exists() or not readme.read_text(encoding="utf-8").strip():
        issues.append(f"{package_dir.relative_to(ROOT)}: README.md is missing or empty")
        return
    lowered = readme.read_text(encoding="utf-8").lower()
    for phrase in UNSAFE_CLAIMS:
        if phrase in lowered:
            issues.append(f"{package_dir.relative_to(ROOT)}: README contains unsafe claim phrase {phrase!r}")


def _check_files(package_dir: Path, issues: list[str]) -> None:
    for file_name in _git_files(package_dir):
        lowered = file_name.lower()
        if any(part in lowered for part in FORBIDDEN_FILE_PARTS):
            issues.append(f"{package_dir.relative_to(ROOT)}: tracked package file should not ship: {file_name}")


def check_python_package(package_dir: Path) -> list[str]:
    issues: list[str] = []
    pyproject = package_dir / "pyproject.toml"
    if not pyproject.exists():
        return [f"{package_dir.relative_to(ROOT)}: pyproject.toml is missing"]
    project = _read_toml(pyproject).get("project", {})
    for field in ("name", "version", "description", "readme", "license"):
        if not project.get(field):
            issues.append(f"{package_dir.relative_to(ROOT)}: project.{field} is required")
    urls = project.get("urls", {})
    if not urls.get("Repository"):
        issues.append(f"{package_dir.relative_to(ROOT)}: project.urls.Repository is required")
    readme_path = package_dir / str(project.get("readme", "README.md"))
    if not readme_path.exists():
        issues.append(f"{package_dir.relative_to(ROOT)}: declared readme does not exist")
    _check_readme(package_dir, issues)
    _check_files(package_dir, issues)
    return issues


def check_npm_package(package_dir: Path) -> list[str]:
    issues: list[str] = []
    package_json = package_dir / "package.json"
    if not package_json.exists():
        return [f"{package_dir.relative_to(ROOT)}: package.json is missing"]
    payload = json.loads(package_json.read_text(encoding="utf-8"))
    for field in ("name", "version", "description", "license", "repository", "files"):
        if not payload.get(field):
            issues.append(f"{package_dir.relative_to(ROOT)}: package.json field {field} is required")
    files = payload.get("files") or []
    if "dist" not in files or "README.md" not in files:
        issues.append(f"{package_dir.relative_to(ROOT)}: files must include dist and README.md")
    _check_readme(package_dir, issues)
    _check_files(package_dir, issues)
    return issues


def check_all() -> list[str]:
    issues: list[str] = []
    for package_dir in PYTHON_PACKAGES:
        issues.extend(check_python_package(package_dir))
    for package_dir in NPM_PACKAGES:
        issues.extend(check_npm_package(package_dir))
    return issues


def main() -> int:
    issues = check_all()
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2))
        return 1
    print(json.dumps({"ok": True, "python_packages": 3, "npm_packages": len(NPM_PACKAGES)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
