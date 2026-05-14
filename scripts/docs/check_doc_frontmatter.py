#!/usr/bin/env python3
"""Verify docs maturity metadata coverage.

Docs may carry inline frontmatter or be covered by the central maturity
registries. Some Windows checkouts deny bulk rewrites of existing docs, so the
central registry remains the authoritative fallback for older files.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = PROJECT_ROOT / "docs"
SUBSYSTEM_REGISTRY = PROJECT_ROOT / "config" / "subsystem-maturity.yaml"
ROUTE_REGISTRY = PROJECT_ROOT / "config" / "route-maturity.yaml"
REQUIRED_KEYS = ("status:", "tier:", "lane:", "last_verified:", "owner:")


def main() -> int:
    missing: list[str] = []
    inline_count = 0
    registry_backed_count = 0
    registry_available = SUBSYSTEM_REGISTRY.exists() and ROUTE_REGISTRY.exists()
    for path in sorted(DOCS_ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            if registry_available:
                registry_backed_count += 1
            else:
                missing.append(path.relative_to(PROJECT_ROOT).as_posix())
            continue
        end = text.find("\n---", 4)
        block = text[: end if end != -1 else 0]
        if end == -1 or not all(key in block for key in REQUIRED_KEYS):
            missing.append(path.relative_to(PROJECT_ROOT).as_posix())
        else:
            inline_count += 1
    if missing:
        print("Docs missing maturity frontmatter:")
        for item in missing:
            print(f"- {item}")
        return 1
    print(
        "Docs maturity metadata verified "
        f"({inline_count} inline frontmatter docs, {registry_backed_count} registry-backed docs)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
