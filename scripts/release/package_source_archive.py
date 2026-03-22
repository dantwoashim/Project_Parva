#!/usr/bin/env python3
"""Create a clean source archive for release distribution."""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

if sys.version_info < (3, 11):  # pragma: no cover - script is pinned to 3.11 in docs
    raise SystemExit("package_source_archive.py requires Python 3.11+")

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
DIST_DIR = PROJECT_ROOT / "dist"

EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    ".venv311",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".playwright-cli",
    "__pycache__",
    "node_modules",
    ".vite",
    "dist",
    "output",
    "reports",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".zip"}
EXCLUDED_RELATIVE_PREFIXES = {
    Path("benchmark/results"),
    Path("backend/data/snapshots"),
    Path("backend/data/traces"),
    Path("backend/project_parva.egg-info"),
}
EXCLUDED_RELATIVE_PATHS = {
    Path("SKILL.md"),
    Path("docs/PARVA_UI_UX_TRUST_RESEARCH_2026-03-14.md"),
    Path("docs/PROJECT_AUDIT_2026-03-13.md"),
    Path("docs/PROJECT_DEEP_AUDIT_2026-03-14.md"),
}
ALLOWED_GENERATED_DIRTY_PATHS = {
    Path("docs/public_beta/authority_dashboard.json"),
    Path("docs/public_beta/authority_dashboard.md"),
    Path("docs/public_beta/dashboard_metrics.json"),
    Path("docs/public_beta/dashboard_metrics.md"),
    Path("docs/public_beta/month9_release_dossier.md"),
}


def _project_version() -> str:
    payload = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def _should_skip(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)

    if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
        return True

    if any(part.startswith(".verify") for part in relative.parts):
        return True

    if any(relative == prefix or prefix in relative.parents for prefix in EXCLUDED_RELATIVE_PREFIXES):
        return True

    if relative in EXCLUDED_RELATIVE_PATHS:
        return True

    if path.suffix in EXCLUDED_SUFFIXES:
        return True

    return False


def _dirty_paths() -> list[Path] | None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None

    dirty_paths: list[Path] = []
    for line in result.stdout.splitlines():
        raw_path = line[3:].strip()
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        if raw_path:
            dirty_paths.append(Path(raw_path))
    return dirty_paths


def _working_tree_is_clean() -> bool:
    dirty_paths = _dirty_paths()
    if dirty_paths is None:
        return True
    if not dirty_paths:
        return True
    return all(path in ALLOWED_GENERATED_DIRTY_PATHS for path in dirty_paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow archiving from a dirty worktree. Intended for local debugging only.",
    )
    args = parser.parse_args(argv)

    if not args.allow_dirty and not _working_tree_is_clean():
        raise SystemExit(
            "Refusing to package from a dirty worktree. Commit or stash changes, or rerun with --allow-dirty for local debugging."
        )

    version = _project_version()
    archive_root = f"project-parva-{version}"
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = DIST_DIR / f"{archive_root}-source.zip"

    files_written = 0
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(PROJECT_ROOT.rglob("*")):
            if not path.is_file() or _should_skip(path):
                continue
            relative = path.relative_to(PROJECT_ROOT)
            archive.write(path, arcname=str(Path(archive_root) / relative))
            files_written += 1

    print(f"Wrote {archive_path} ({files_written} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
