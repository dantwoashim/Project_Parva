#!/usr/bin/env python3
"""Scan tracked text files for likely hard-coded credentials."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SELF_PATH = Path(__file__).resolve()
SKIP_PREFIXES = (
    "data/source_archive/",
    "docs/contracts/",
)
SKIP_FILES = {
    "frontend/package-lock.json",
}
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
ALLOWLIST_PATTERNS = (
    re.compile(r"parva-test-(?:admin|read)-token", re.IGNORECASE),
    re.compile(r"parva-test-read-key", re.IGNORECASE),
    re.compile(r"change-me", re.IGNORECASE),
    re.compile(r"https://github\.com/example/project-parva", re.IGNORECASE),
    re.compile(r"https://example\.com/", re.IGNORECASE),
    re.compile(r"http://localhost", re.IGNORECASE),
    re.compile(r"http://127\.0\.0\.1", re.IGNORECASE),
)
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "Hard-coded credential assignment",
        re.compile(
            r"(?i)(?<![\w.])(api[_-]?key|secret|token|password|passwd)\b.{0,20}[:=].{0,5}[\"'](?!\{)[^\"'\s]{12,}[\"']"
        ),
    ),
    (
        "Authorization bearer literal",
        re.compile(r"(?i)authorization[\"']?\s*[:=]\s*[\"']bearer [^\"'\s]{12,}[\"']"),
    ),
    (
        "Credential-bearing URL",
        re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp|smtp)://[^/\s:@]+:[^/\s@]+@"),
    ),
    (
        "Private key block",
        re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----"),
    ),
)


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for raw in result.stdout.splitlines():
        rel = raw.strip()
        if not rel:
            continue
        files.append(PROJECT_ROOT / rel)
    return files


def _is_skipped(path: Path) -> bool:
    rel = path.relative_to(PROJECT_ROOT).as_posix()
    if rel in SKIP_FILES:
        return True
    if rel == SELF_PATH.relative_to(PROJECT_ROOT).as_posix():
        return True
    return any(rel.startswith(prefix) for prefix in SKIP_PREFIXES)


def _is_binary(path: Path) -> bool:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    try:
        return b"\x00" in path.read_bytes()[:4096]
    except OSError:
        return True


def _is_allowed(line: str) -> bool:
    return any(pattern.search(line) for pattern in ALLOWLIST_PATTERNS)


def _print_line(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write((text + "\n").encode(encoding, errors="backslashreplace"))
        sys.stdout.flush()


def main() -> int:
    findings: list[str] = []

    for path in _tracked_files():
        if _is_skipped(path) or _is_binary(path):
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        rel = path.relative_to(PROJECT_ROOT).as_posix()
        for line_number, line in enumerate(lines, start=1):
            if _is_allowed(line):
                continue
            for label, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(f"{rel}:{line_number}: {label}")
                    break

    if findings:
        for finding in findings:
            _print_line(finding)
        return 1

    print("No hard-coded secrets detected in tracked source files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
