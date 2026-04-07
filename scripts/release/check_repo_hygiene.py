#!/usr/bin/env python3
"""Reject known workspace residue and tracked release artifacts in the repo."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DISALLOWED_TRACKED_PREFIXES = {
    Path("benchmark/results"),
    Path("backend/data/snapshots"),
    Path("backend/data/traces"),
    Path("output"),
    Path("reports"),
    Path("tmp"),
}
DISALLOWED_TRACKED_EXACT = {
    Path("evaluation.csv"),
    Path("backend/evaluation.csv"),
}
DISALLOWED_TRACKED_SEGMENTS = {
    ".mypy_cache",
    ".playwright-cli",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "dist",
    "node_modules",
}
DISALLOWED_TRACKED_FILENAMES = {
    ".DS_Store",
}
DISALLOWED_TRACKED_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _tracked_path_issue(tracked: str) -> str | None:
    relative = Path(tracked)

    if relative in DISALLOWED_TRACKED_EXACT:
        return f"Tracked generated artifact must not live in source control: {tracked}"

    if any(relative == prefix or prefix in relative.parents for prefix in DISALLOWED_TRACKED_PREFIXES):
        return f"Tracked release artifact must not live in source control: {tracked}"

    if relative.name in DISALLOWED_TRACKED_FILENAMES or relative.suffix in DISALLOWED_TRACKED_SUFFIXES:
        return f"Tracked local/runtime artifact must not live in source control: {tracked}"

    for part in relative.parts:
        if part in DISALLOWED_TRACKED_SEGMENTS or part.startswith(".venv") or part.startswith(".verify"):
            return f"Tracked release artifact must not live in source control: {tracked}"
        if part.endswith(".egg-info"):
            return f"Tracked packaging residue must not live in source control: {tracked}"

    return None


def main() -> int:
    issues: list[str] = []

    root_package = PROJECT_ROOT / "package.json"
    if root_package.exists():
        payload = _load_json(root_package)
        if payload.get("name") == "viral-sync-workspace":
            issues.append("Root package.json still identifies the repo as viral-sync-workspace.")
        workspaces = payload.get("workspaces") or []
        if any(item in {"app", "relayer", "server/actions", "cranks", "packages/*"} for item in workspaces):
            issues.append("Root package.json still declares unrelated viral-sync workspaces.")

    legacy_shared_package = PROJECT_ROOT / "packages" / "shared" / "package.json"
    if legacy_shared_package.exists():
        payload = _load_json(legacy_shared_package)
        package_name = str(payload.get("name") or "")
        if package_name.startswith("@viral-sync/"):
            issues.append("packages/shared/package.json still exports the unrelated @viral-sync package.")

    legacy_shared_source = PROJECT_ROOT / "packages" / "shared" / "src" / "index.ts"
    if legacy_shared_source.exists():
        source_text = legacy_shared_source.read_text(encoding="utf-8")
        if "LAMPORTS_PER_SOL" in source_text or "RELAYER_ROUTE_PREFIX" in source_text:
            issues.append("packages/shared/src/index.ts still contains unrelated relayer/Solana exports.")

    root_tsconfig = PROJECT_ROOT / "tsconfig.json"
    if root_tsconfig.exists():
        text = root_tsconfig.read_text(encoding="utf-8")
        if "packages/shared" in text or '"mocha"' in text:
            issues.append("Root tsconfig.json still references unrelated workspace test settings.")

    root_tsconfig_base = PROJECT_ROOT / "tsconfig.base.json"
    if root_tsconfig_base.exists():
        issues.append("Root tsconfig.base.json still exists even though Parva does not use a root TS workspace.")

    for tracked in _tracked_files():
        issue = _tracked_path_issue(tracked)
        if issue:
            issues.append(issue)

    if issues:
        for issue in issues:
            print(f"[repo-hygiene] {issue}")
        raise SystemExit(1)

    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
