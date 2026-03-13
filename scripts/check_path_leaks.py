#!/usr/bin/env python3
"""Fail if repository files contain leaked local machine paths."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SELF_PATH = Path(__file__).resolve()
SKIP_DIRS = {
    ".git",
    ".venv",
    ".venv311",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}
PATTERNS = (
    "/Users/",
    "C:\\Users\\",
    "/home/",
)


def _is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except Exception:
        return True
    return b"\x00" in chunk


def main() -> int:
    matches: list[tuple[Path, int, str]] = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.resolve() == SELF_PATH:
            continue
        if any(part in SKIP_DIRS or part.startswith(".verify") for part in path.parts):
            continue
        if _is_binary(path):
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(lines, start=1):
            if any(pattern in line for pattern in PATTERNS):
                matches.append((path.relative_to(PROJECT_ROOT), line_number, line.strip()))

    if not matches:
        print("No local path leaks detected.")
        return 0

    for rel_path, line_number, line in matches:
        print(f"{rel_path}:{line_number}: {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
