#!/usr/bin/env python3
"""Scan public-facing text for unsupported authority and adoption claims."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "frontend" / "src",
    PROJECT_ROOT / "packages" / "parva-python" / "README.md",
    PROJECT_ROOT / "packages" / "parva-js" / "README.md",
    PROJECT_ROOT / "packages" / "parva-ai-tools" / "README.md",
    PROJECT_ROOT / "packages" / "parva-mcp-server" / "README.md",
)

SKIP_PARTS = {
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
}

FORBIDDEN_PATTERNS = {
    "official government": re.compile(r"\bofficial\s+government\b", re.IGNORECASE),
    "government approved": re.compile(r"\bgovernment[-\s]+approved\b", re.IGNORECASE),
    "legal authority": re.compile(r"\blegal\s+authority\b", re.IGNORECASE),
    "banking authority": re.compile(r"\bbanking\s+authority\b", re.IGNORECASE),
    "payroll authority": re.compile(r"\bpayroll\s+authority\b", re.IGNORECASE),
    "tax authority": re.compile(r"\btax\s+authority\b", re.IGNORECASE),
    "official future BS": re.compile(r"\bofficial\s+future\s+BS\b", re.IGNORECASE),
    "guaranteed future": re.compile(r"\bguaranteed\s+future\b", re.IGNORECASE),
    "Panchanga replacement": re.compile(r"\bPanchanga\s+replacement\b", re.IGNORECASE),
    "certified": re.compile(r"\bcertified\b", re.IGNORECASE),
    "SOC 2": re.compile(r"\bSOC\s*2\b", re.IGNORECASE),
}

NEGATION_PATTERNS = (
    re.compile(r"\bnot\b", re.IGNORECASE),
    re.compile(r"\bno\b", re.IGNORECASE),
    re.compile(r"\bnever\s+claim\b", re.IGNORECASE),
    re.compile(r"\bdoes\s+not\b", re.IGNORECASE),
    re.compile(r"\bmust\s+not\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+claiming\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+treating\b", re.IGNORECASE),
    re.compile(r"\bthey\s+are\s+not\b", re.IGNORECASE),
    re.compile(r"\bdisallowed\s+public\s+claims\b", re.IGNORECASE),
    re.compile(r"\ba\s+replacement\s+for\b", re.IGNORECASE),
)


def _candidate_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            if path.suffix.lower() not in {".md", ".mdx", ".js", ".jsx", ".ts", ".tsx", ".json"}:
                continue
            files.append(path)
    return sorted(set(files))


def _is_negated(line: str, start: int, previous_context: str = "") -> bool:
    window = f"{previous_context}\n{line[max(0, start - 160) : start + 100]}"
    return any(pattern.search(window) for pattern in NEGATION_PATTERNS)


def check_public_claims() -> list[str]:
    issues: list[str] = []
    for path in _candidate_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lines = text.splitlines()
        for line_number, line in enumerate(lines, start=1):
            previous_context = "\n".join(lines[max(0, line_number - 9) : line_number - 1])
            for label, pattern in FORBIDDEN_PATTERNS.items():
                for match in pattern.finditer(line):
                    if _is_negated(line, match.start(), previous_context):
                        continue
                    rel = path.relative_to(PROJECT_ROOT).as_posix()
                    issues.append(f"{rel}:{line_number}: unsupported public claim phrase `{label}`")
    return issues


def main() -> int:
    issues = check_public_claims()
    if issues:
        for issue in issues:
            print(f"[public-claims] {issue}")
        return 1
    print("Public claims check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
