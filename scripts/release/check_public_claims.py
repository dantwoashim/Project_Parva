#!/usr/bin/env python3
"""Scan public-facing text for unsupported authority and adoption claims."""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs",
    PROJECT_ROOT / "examples",
    PROJECT_ROOT / "reports",
    PROJECT_ROOT / "frontend" / "src",
    PROJECT_ROOT / "packages" / "parva-python",
    PROJECT_ROOT / "packages" / "parva-js",
    PROJECT_ROOT / "packages" / "parva-local-kernel",
    PROJECT_ROOT / "packages" / "parva-agent-tools",
    PROJECT_ROOT / "packages" / "parva-mcp-server",
)

SKIP_PARTS = {
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "external_reviewer_dry_run",
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
    "published package": re.compile(r"\b(published|available)\s+on\s+(npm|PyPI)\b", re.IGNORECASE),
    "MCP registry acceptance": re.compile(r"\bMCP\s+registry\s+(accepted|approved|listed)\b", re.IGNORECASE),
    "customer adoption": re.compile(r"\b(customer|adoption|pilot\s+customer)\s+(proof|validated|confirmed)\b", re.IGNORECASE),
    "official Panchanga authority": re.compile(r"\bofficial\s+Panchanga\s+authority\b", re.IGNORECASE),
    "ritual final authority": re.compile(r"\britual\s+final\s+authority\b", re.IGNORECASE),
    "JPL-backed overclaim": re.compile(r"\bJPL[-\s]+backed\b", re.IGNORECASE),
    "static lookup source-backed": re.compile(r"\bstatic\s+lookup\b.{0,80}\bsource[-\s]+backed\b", re.IGNORECASE),
}

OPENAPI_OPERATION_CLAIM_PATTERNS = {
    "authoritative": re.compile(r"\bauthoritative\b", re.IGNORECASE),
    "production-safe": re.compile(r"\bproduction[-\s]+safe\b", re.IGNORECASE),
    "enterprise-ready": re.compile(r"\benterprise[-\s]+ready\b", re.IGNORECASE),
    "verified": re.compile(r"\bverified\b", re.IGNORECASE),
    "source-backed": re.compile(r"\bsource[-\s]+backed\b", re.IGNORECASE),
}

NEGATION_PATTERNS = (
    re.compile(r"\bnot\b", re.IGNORECASE),
    re.compile(r"\bno\b", re.IGNORECASE),
    re.compile(r"\bnever\s+claim\b", re.IGNORECASE),
    re.compile(r"\bdo\s+not\s+claim\b", re.IGNORECASE),
    re.compile(r"\bmust\s+not\s+say\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+cannot\s+be\s+claimed\b", re.IGNORECASE),
    re.compile(r"\bforbidden\s+claims\b", re.IGNORECASE),
    re.compile(r"\bnot_claimable\b", re.IGNORECASE),
    re.compile(r"\bdoes\s+not\b", re.IGNORECASE),
    re.compile(r"\bmust\s+not\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+claiming\b", re.IGNORECASE),
    re.compile(r"\bwithout\s+treating\b", re.IGNORECASE),
    re.compile(r"\bthey\s+are\s+not\b", re.IGNORECASE),
    re.compile(r"\bdisallowed\s+public\s+claims\b", re.IGNORECASE),
    re.compile(r"\ba\s+replacement\s+for\b", re.IGNORECASE),
    re.compile(r"\bcannot\b", re.IGNORECASE),
    re.compile(r"\bcannot\s+replace\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+JPL\s+cannot\s+decide\b", re.IGNORECASE),
    re.compile(r"\bunless\s+actually\b", re.IGNORECASE),
    re.compile(r"\bunless\s+real\b", re.IGNORECASE),
    re.compile(r"\bonly\s+when\b", re.IGNORECASE),
    re.compile(r"\bis\s+claimed\s+only\s+when\b", re.IGNORECASE),
    re.compile(r"\bnot\s+real\s+JPL\b", re.IGNORECASE),
    re.compile(r"\bno\s+real\s+JPL\b", re.IGNORECASE),
    re.compile(r"\bwhat\s+JPL[-\s]+backed\s+means\b", re.IGNORECASE),
    re.compile(r"\bJPL[-\s]+backed\s+claim\b", re.IGNORECASE),
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


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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
                    rel = _display_path(path)
                    issues.append(f"{rel}:{line_number}: unsupported public claim phrase `{label}`")
    issues.extend(_check_openapi_operation_claims())
    return issues


def _check_openapi_operation_claims() -> list[str]:
    issues: list[str] = []
    for path in sorted((PROJECT_ROOT / "docs" / "api-docs").glob("openapi*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for route_path, methods in (document.get("paths") or {}).items():
            if not isinstance(methods, dict):
                continue
            for method, operation in methods.items():
                if not isinstance(operation, dict):
                    continue
                text = "\n".join(
                    str(operation.get(key) or "") for key in ("summary", "description")
                )
                if not text.strip():
                    continue
                for label, pattern in OPENAPI_OPERATION_CLAIM_PATTERNS.items():
                    for match in pattern.finditer(text):
                        if _is_negated(text, match.start()):
                            continue
                        rel = path.relative_to(PROJECT_ROOT).as_posix()
                        issues.append(
                            f"{rel}:{method.upper()} {route_path}: "
                            f"unsupported OpenAPI operation claim `{label}`"
                        )
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
