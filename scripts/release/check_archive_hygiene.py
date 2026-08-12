#!/usr/bin/env python3
"""Validate that git source archives are coherent public review artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_ARCHIVE_PARTS = (
    ".git",
    "node_modules",
    "frontend/dist",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "output",
    "tmp",
)
FORBIDDEN_SUFFIXES = (".zip", ".tgz")
REQUIRED_ARCHIVE_PATHS = (
    "README.md",
    "docs/QUICKSTART.md",
    "docs/releases/v0.3.0-public-readiness.md",
    "docs/releases/PACKAGE_PUBLISHING.md",
    "public-benchmark/README.md",
    "public-benchmark/results/comparison.json",
    "public-benchmark/results/benchmark.svg",
    "reports/red_check_closure/README.md",
)


def _run(command: list[str], *, cwd: Path = PROJECT_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def _tracked_files() -> list[str]:
    result = _run(["git", "ls-files"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_tracked_junk() -> list[str]:
    issues: list[str] = []
    for path in _tracked_files():
        lowered = path.lower()
        if any(part in lowered.split("/") for part in {".git", "node_modules", "__pycache__"}):
            issues.append(f"{path}: forbidden tracked archive path")
        if any(part in lowered for part in ("frontend/dist/", ".pytest_cache/", ".ruff_cache/", "output/", "tmp/")):
            issues.append(f"{path}: forbidden tracked archive path")
        if lowered.endswith(FORBIDDEN_SUFFIXES):
            issues.append(f"{path}: source archive must not contain nested archive files")
    return issues


def check_required_paths(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_ARCHIVE_PATHS:
        path = root / rel_path
        if not path.exists():
            issues.append(f"{rel_path}: missing from source archive")
        elif path.is_file() and path.stat().st_size == 0:
            issues.append(f"{rel_path}: empty in source archive")
    return issues


def check_readme_report_links(root: Path) -> list[str]:
    issues: list[str] = []
    readme = root / "README.md"
    if not readme.exists():
        return ["README.md: missing from archive"]
    text = readme.read_text(encoding="utf-8")
    for rel_path in REQUIRED_ARCHIVE_PATHS:
        if rel_path.startswith("reports/") and rel_path in text and not (root / rel_path).exists():
            issues.append(f"README.md links {rel_path}, but archive does not include it")
    return issues


def _safe_extract_tar(archive: tarfile.TarFile, destination: Path) -> None:
    destination_root = destination.resolve()
    for member in archive.getmembers():
        member_path = (destination / member.name).resolve()
        if destination_root != member_path and destination_root not in member_path.parents:
            raise RuntimeError(f"Archive member escapes extraction root: {member.name}")
        if member.isdir():
            member_path.mkdir(parents=True, exist_ok=True)
            continue
        if not member.isfile():
            raise RuntimeError(f"Archive member is not a regular file: {member.name}")
        member_path.parent.mkdir(parents=True, exist_ok=True)
        with archive.extractfile(member) as source, member_path.open("wb") as target:
            if source is None:
                raise RuntimeError(f"Archive member cannot be read: {member.name}")
            shutil.copyfileobj(source, target)


def check_git_archive() -> list[str]:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="parva-archive-") as tmp:
        tmp_path = Path(tmp)
        archive_path = tmp_path / "source.tar"
        result = _run(["git", "archive", "--format=tar", "HEAD", "-o", str(archive_path)])
        if result.returncode != 0:
            return [f"git archive HEAD failed: {result.stderr or result.stdout}"]
        extract_root = tmp_path / "extract"
        extract_root.mkdir()
        with tarfile.open(archive_path) as archive:
            _safe_extract_tar(archive, extract_root)

        for path in extract_root.rglob("*"):
            rel = path.relative_to(extract_root).as_posix().lower()
            if any(part in rel.split("/") for part in (".git", "node_modules", "__pycache__")):
                issues.append(f"{rel}: forbidden path in archive")
            if any(fragment in rel for fragment in ("frontend/dist/", ".pytest_cache/", ".ruff_cache/", "output/", "tmp/")):
                issues.append(f"{rel}: forbidden path in archive")
            if rel.endswith(FORBIDDEN_SUFFIXES):
                issues.append(f"{rel}: nested archive file in archive")

        issues.extend(check_required_paths(extract_root))
        issues.extend(check_readme_report_links(extract_root))
    return issues


def check_archive_hygiene(*, run_archive: bool = True) -> list[str]:
    issues = check_tracked_junk()
    if run_archive:
        issues.extend(check_git_archive())
    return sorted(set(issues))


def main() -> int:
    issues = check_archive_hygiene(run_archive=True)
    if issues:
        print(json.dumps({"ok": False, "issues": issues}, indent=2))
        return 1
    print(json.dumps({"ok": True, "required_paths": len(REQUIRED_ARCHIVE_PATHS)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
