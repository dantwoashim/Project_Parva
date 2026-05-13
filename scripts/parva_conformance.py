#!/usr/bin/env python3
"""Run Parva Protocol conformance checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.protocol_service import ProtocolError, run_conformance_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="local")
    parser.add_argument("--level", default="parva_core")
    args = parser.parse_args()
    try:
        report = run_conformance_payload(target=args.target, level=args.level)
    except ProtocolError as exc:
        print(json.dumps({"status": "fail", "error": str(exc), "code": exc.code}, indent=2))
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
