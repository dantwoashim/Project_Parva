#!/usr/bin/env python3
"""Scan public surfaces for private route and authority-boundary leakage."""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = [
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "AGENTS.md",
    PROJECT_ROOT / "llms.txt",
    PROJECT_ROOT / "llms-full.txt",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "examples",
    PROJECT_ROOT / "reports",
    PROJECT_ROOT / ".github" / "workflows",
    PROJECT_ROOT / "frontend" / "src",
    PROJECT_ROOT / "packages" / "parva-python",
    PROJECT_ROOT / "packages" / "parva-js",
    PROJECT_ROOT / "packages" / "parva-local-kernel",
    PROJECT_ROOT / "packages" / "parva-ai-tools",
    PROJECT_ROOT / "packages" / "parva-mcp-server",
]

INVENTORY_DOCS = {
    "docs/ROUTE_ACCESS.md",
}

SKIP_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".vite",
    "external_reviewer_dry_run",
}

TEXT_EXTS = {".md", ".txt", ".json", ".js", ".jsx", ".ts", ".tsx", ".py", ".yml", ".yaml"}

PRIVATE_ROUTE_PATTERNS = {
    "private route": re.compile(r"/v\d+/api/(?:admin|billing|private|research|internal)(?:/|\b)", re.IGNORECASE),
    "future exact research": re.compile(r"/v\d+/api/future-bs/(?:exact|research|private)", re.IGNORECASE),
}

BOUNDARY_PATTERNS = {
    "official panchanga authority": re.compile(r"\bofficial\s+panchanga\s+authority\b", re.IGNORECASE),
    "ritual final authority": re.compile(r"\britual\s+final\s+authority\b", re.IGNORECASE),
    "jpl-backed without fixture": re.compile(r"\bJPL[-\s]+backed\b", re.IGNORECASE),
}

SAFE_NEGATION = re.compile(
    r"\b(no|not|never|without|does\s+not|must\s+not|must\s+not\s+say|do\s+not\s+claim|cannot|unless|forbidden\s+claims|what\s+cannot\s+be\s+claimed)\b",
    re.IGNORECASE,
)
JPL_EVIDENCE = re.compile(r"\b(fixture|kernel|hash|configured|optional|setup)\b", re.IGNORECASE)


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
                continue
            if "docs" in path.parts and "api-docs" in path.parts:
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            files.append(path)
    return sorted(set(files))


def _line_is_safe(line: str, match_start: int, previous_context: str = "", *, jpl: bool = False) -> bool:
    window = f"{previous_context}\n{line[max(0, match_start - 120) : match_start + 160]}"
    if SAFE_NEGATION.search(window):
        return True
    if jpl and JPL_EVIDENCE.search(window):
        return True
    return False


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _check_text_files() -> list[str]:
    issues: list[str] = []
    for path in _iter_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        rel = _display_path(path)
        if rel in INVENTORY_DOCS:
            continue
        for lineno, line in enumerate(lines, start=1):
            previous_context = "\n".join(lines[max(0, lineno - 8) : lineno - 1])
            for label, pattern in PRIVATE_ROUTE_PATTERNS.items():
                for match in pattern.finditer(line):
                    if _line_is_safe(line, match.start(), previous_context):
                        continue
                    issues.append(f"{rel}:{lineno}: public surface exposes {label}")
            for label, pattern in BOUNDARY_PATTERNS.items():
                for match in pattern.finditer(line):
                    if _line_is_safe(line, match.start(), previous_context, jpl=label.startswith("jpl")):
                        continue
                    issues.append(f"{rel}:{lineno}: unsafe public claim `{label}`")
    return issues


def _check_openapi_public_profile() -> list[str]:
    path = PROJECT_ROOT / "docs" / "api-docs" / "openapi.public-reference.json"
    if not path.exists():
        return [f"{path.relative_to(PROJECT_ROOT)}: missing public OpenAPI profile"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    issues = []
    for route in (payload.get("paths") or {}):
        if re.search(r"/(?:admin|billing|private|research|internal)(?:/|$)", route, re.IGNORECASE):
            issues.append(f"docs/api-docs/openapi.public-reference.json: public OpenAPI leaks {route}")
    return issues


def main() -> int:
    issues = _check_text_files() + _check_openapi_public_profile()
    if issues:
        for issue in issues:
            print(f"[public-surface-security] {issue}")
        return 1
    print("Public surface security check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
