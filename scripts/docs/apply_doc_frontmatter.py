#!/usr/bin/env python3
"""Apply minimal maturity frontmatter to Markdown docs that do not have it."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = PROJECT_ROOT / "docs"
TODAY = "2026-05-14"


def classify(path: Path) -> tuple[str, int, str, str]:
    relative = path.relative_to(DOCS_ROOT).as_posix().lower()
    name = path.name.lower()
    if relative.startswith(("internal_audit/", "internal_archive/", "external_audit/")):
        return "historical", 4, "docs", "docs-team"
    if relative.startswith("future_bs/"):
        return "research", 3, "research", "research-team"
    if "protocol" in relative or "conformance" in relative or "credential" in relative:
        return "draft", 2, "protocol", "protocol-team"
    if any(token in relative for token in ("security", "billing", "deployment", "observability", "sre", "rollback")):
        return "stable", 1, "operations", "platform-team"
    if any(token in relative for token in ("sdk", "embed", "quickstart", "api_reference", "versioning", "development")):
        return "public-beta", 1, "dx", "dx-team"
    if any(token in name for token in ("government", "vendor", "ecosystem", "community", "pilot")):
        return "draft", 2, "protocol", "product-team"
    return "public-beta", 1, "core", "platform-team"


def frontmatter_for(path: Path) -> str:
    status, tier, lane, owner = classify(path)
    return (
        "---\n"
        f"status: {status}\n"
        f"tier: {tier}\n"
        f"lane: {lane}\n"
        f"last_verified: {TODAY}\n"
        f"owner: {owner}\n"
        "---\n\n"
    )


def main() -> int:
    changed = 0
    for path in sorted(DOCS_ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            continue
        path.write_text(frontmatter_for(path) + text, encoding="utf-8")
        changed += 1
    print(f"Applied doc frontmatter to {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
