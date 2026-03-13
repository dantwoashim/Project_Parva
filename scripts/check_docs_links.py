#!/usr/bin/env python3
"""Validate repo-relative file references in README and docs."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOC_FILES = [PROJECT_ROOT / "README.md", *sorted((PROJECT_ROOT / "docs").rglob("*.md"))]
PATH_PATTERN = re.compile(
    r"`(/?(?:docs|scripts|data|backend|frontend|tests|reports|benchmark)/[A-Za-z0-9_./-]+)`"
)


def _normalize(raw: str) -> str:
    return raw.rstrip("`.,)").lstrip("/")


def main() -> int:
    failures: list[str] = []

    for doc in DOC_FILES:
        lines = doc.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            for raw in PATH_PATTERN.findall(line):
                rel_path = _normalize(raw)
                if rel_path.startswith("reports/"):
                    if doc.name == "GENERATED_ARTIFACTS.md":
                        continue
                    if "generated artifact" not in line.lower():
                        failures.append(
                            f"{doc.relative_to(PROJECT_ROOT)}:{line_number}: "
                            f"{rel_path} must be labeled as a generated artifact"
                        )
                    continue

                if not (PROJECT_ROOT / rel_path).exists():
                    failures.append(
                        f"{doc.relative_to(PROJECT_ROOT)}:{line_number}: missing path {rel_path}"
                    )

    if failures:
        print("\n".join(failures))
        return 1

    print("Documentation links verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
