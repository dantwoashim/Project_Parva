#!/usr/bin/env python3
"""Scan source files for obvious committed secrets."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv311",
    ".verify",
    ".nox",
    ".tox",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "output",
    "reports",
    "tmp",
    "venv",
}
EXCLUDED_PREFIXES = {
    Path("backend/data/snapshots"),
    Path("backend/data/traces"),
    Path("frontend/dist"),
}
TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".csv",
    ".env",
    ".example",
    ".html",
    ".ics",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".lock",
    ".md",
    ".mjs",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b")),
    ("sk-prefixed api key", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("sk-ant-prefixed api key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{32,}\b")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "generic assigned secret",
        re.compile(
            r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*"
            r"['\"]?(?!changeme|change-me|example|placeholder|test|dummy|local|<|\\$)"
            r"[A-Za-z0-9_./+=:@-]{24,}['\"]?"
        ),
    ),
)


def _is_excluded(path: Path) -> bool:
    relative = path.relative_to(PROJECT_ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return True
    return any(relative == prefix or prefix in relative.parents for prefix in EXCLUDED_PREFIXES)


def _is_text_candidate(path: Path) -> bool:
    if path.name.startswith(".env"):
        return True
    if path.suffix in TEXT_SUFFIXES:
        return True
    return path.name in {"Makefile", "Dockerfile", "Dockerfile.cloudrun"}


def _scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    failures: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if "nosec" in line or "pragma: allowlist secret" in line:
            continue
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                rel = path.relative_to(PROJECT_ROOT)
                failures.append(f"{rel}:{line_number}: possible {label}")
    return failures


def _candidate_paths() -> list[Path]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        completed = None

    if completed is not None and completed.returncode == 0:
        return sorted(PROJECT_ROOT / item for item in completed.stdout.split("\0") if item)
    return sorted(PROJECT_ROOT.rglob("*"))


def main() -> int:
    failures: list[str] = []
    for path in _candidate_paths():
        if not path.is_file() or _is_excluded(path) or not _is_text_candidate(path):
            continue
        failures.extend(_scan_file(path))

    if failures:
        print("\n".join(failures))
        return 1

    print("Secret scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
