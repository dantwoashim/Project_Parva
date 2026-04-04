#!/usr/bin/env python3
"""Fail if repository files contain leaked local machine paths."""

from __future__ import annotations

from pathlib import Path
import re
import sys

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
REGEX_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9+.-])/Users/[^/\s]+/"),
    re.compile(r"(?<![A-Za-z0-9+.-])/home/[^/\s]+/"),
    re.compile(r"(?<![A-Za-z0-9+.-])[A-Za-z]:\\\\Users\\\\"),
    re.compile(r"(?<![A-Za-z0-9+.-])[A-Za-z]:\\\\"),
    re.compile(r"(?<![A-Za-z0-9+.-])[A-Za-z]:/"),
)
BINARY_SUFFIXES = {
    ".7z",
    ".dll",
    ".eot",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".otf",
    ".pdf",
    ".png",
    ".tar",
    ".ttf",
    ".woff",
    ".woff2",
    ".zip",
}


def _is_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    try:
        chunk = path.read_bytes()[:4096]
    except Exception:
        return True
    return b"\x00" in chunk


def _print_line(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write((text + "\n").encode(encoding, errors="backslashreplace"))
        sys.stdout.flush()


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
            if line.startswith(("http://", "https://")):
                continue
            if any(regex.search(line) for regex in REGEX_PATTERNS):
                matches.append((path.relative_to(PROJECT_ROOT), line_number, line.strip()))

    if not matches:
        print("No local path leaks detected.")
        return 0

    for rel_path, line_number, line in matches:
        _print_line(f"{rel_path}:{line_number}: {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
