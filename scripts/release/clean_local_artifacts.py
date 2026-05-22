"""Safely remove local cache/build artifacts that add audit noise.

The default mode is a dry run. Use ``--apply`` to delete only known ignored
cache paths after tracked-file and repo-boundary checks pass.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

LOCAL_ARTIFACTS = (
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "frontend/.vite",
    "frontend/dist",
    "frontend/node_modules",
    "packages/parva-js/dist",
    "packages/parva-js/node_modules",
    "packages/parva-local-kernel/dist",
    "packages/parva-local-kernel/node_modules",
    "dist",
    "build",
    "coverage",
    "htmlcov",
    "tmp",
)


def _git_lines(*args: str) -> set[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def _is_safe_target(path: Path, tracked: set[str]) -> bool:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return False
    if relative in {"", ".git"} or relative.startswith(".git/"):
        return False
    return relative not in tracked


def clean(*, apply: bool) -> int:
    tracked = _git_lines("ls-files")
    removed = 0
    skipped = 0
    for relative in LOCAL_ARTIFACTS:
        target = REPO_ROOT / relative
        if not target.exists():
            continue
        if not _is_safe_target(target, tracked):
            print(f"SKIP unsafe or tracked path: {relative}")
            skipped += 1
            continue
        action = "REMOVE" if apply else "DRY-RUN"
        print(f"{action} {relative}")
        if apply:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        removed += 1
    print(f"Summary: candidates={removed}, skipped={skipped}, apply={apply}")
    return 1 if skipped else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="delete safe local artifacts")
    args = parser.parse_args()
    return clean(apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())

