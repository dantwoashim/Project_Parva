#!/usr/bin/env python3
"""Compile public claims through the repository public-claims checker."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.release.check_public_claims import check_public_claims  # noqa: E402


def main() -> int:
    issues = check_public_claims()
    if issues:
        for issue in issues:
            print(f"[claim-compiler] {issue}")
        return 1
    print("Public claim compiler passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
