#!/usr/bin/env python3
"""Verify quickstart and SDK example artifacts exist."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = [
    "docs/API_QUICKSTART.md",
    "docs/SDK_USAGE.md",
    "docs/SDK_ROADMAP.md",
    "docs/EMBED_GUIDE.md",
    "docs/FRONTEND_ARCHITECTURE.md",
    "examples/python/convert.py",
    "examples/python/holidays.py",
    "examples/python/verify_bundle.py",
    "examples/javascript/convert.mjs",
    "examples/javascript/holidays.mjs",
    "examples/javascript/protocol-version.mjs",
    "examples/curl/quickstart.sh",
]
REQUIRED_TEXT = {
    "docs/API_QUICKSTART.md": ["curl", "Python SDK example", "JavaScript SDK example"],
    "docs/SDK_USAGE.md": ["Maturity Exposure Policy", "parva today", "packages/parva-python"],
    "docs/SDK_ROADMAP.md": ["Canonical SDKs", "Research private"],
    "docs/EMBED_GUIDE.md": ["data-api-base", "api_base"],
    "docs/FRONTEND_ARCHITECTURE.md": ["capabilityMap.js", "VerificationComponents.jsx"],
}


def main() -> int:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        path = PROJECT_ROOT / relative
        if not path.exists():
            failures.append(f"Missing required artifact: {relative}")
            continue
        if path.stat().st_size == 0:
            failures.append(f"Required artifact is empty: {relative}")

    for relative, needles in REQUIRED_TEXT.items():
        path = PROJECT_ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                failures.append(f"{relative} is missing required text: {needle}")

    if failures:
        print("\n".join(failures))
        return 1

    print("Quickstart and SDK examples verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
