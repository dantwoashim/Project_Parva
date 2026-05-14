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
    parser.add_argument("--artifact", help="Optional conformance fixture JSON to evaluate.")
    parser.add_argument("--output", help="Write the compatibility report JSON to this path.")
    args = parser.parse_args()
    artifact = None
    if args.artifact:
        artifact_path = Path(args.artifact)
        try:
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        except OSError as exc:
            print(json.dumps({"status": "fail", "error": str(exc), "code": "ARTIFACT_READ_FAILED"}, indent=2))
            return 1
        except json.JSONDecodeError as exc:
            print(json.dumps({"status": "fail", "error": str(exc), "code": "ARTIFACT_JSON_INVALID"}, indent=2))
            return 1
    try:
        report = run_conformance_payload(target=args.target, level=args.level, artifact=artifact)
    except ProtocolError as exc:
        print(json.dumps({"status": "fail", "error": str(exc), "code": exc.code}, indent=2))
        return 1
    text = json.dumps(report, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
