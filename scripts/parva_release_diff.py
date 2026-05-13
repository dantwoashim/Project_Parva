#!/usr/bin/env python3
"""Diff two Project Parva public release manifests."""

# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.trust_infrastructure_service import (
    TrustInfrastructureError,
    diff_releases_payload,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diff Project Parva public release metadata.")
    parser.add_argument("--from", dest="from_release", required=True)
    parser.add_argument("--to", dest="to_release", required=True)
    args = parser.parse_args(argv)

    try:
        payload = diff_releases_payload(args.from_release, args.to_release)
    except TrustInfrastructureError as exc:
        print(f"release diff failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
