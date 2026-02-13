#!/usr/bin/env python3
"""Replay and verify deterministic integrity of a stored Parva trace."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRACE_DIR = PROJECT_ROOT / "backend" / "data" / "traces"


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay deterministic Parva calculation trace")
    parser.add_argument("trace_id", help="Trace id (e.g. tr_abcd1234...)")
    args = parser.parse_args()

    path = TRACE_DIR / f"{args.trace_id}.json"
    if not path.exists():
        print(json.dumps({"trace_id": args.trace_id, "valid": False, "reason": "trace_not_found"}, indent=2))
        return 1

    payload = json.loads(path.read_text(encoding="utf-8"))

    base = {
        "trace_type": payload.get("trace_type"),
        "subject": payload.get("subject"),
        "inputs": payload.get("inputs"),
        "outputs": payload.get("outputs"),
        "steps": payload.get("steps"),
        "provenance": payload.get("provenance"),
    }
    canonical = json.dumps(base, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    expected = f"tr_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:20]}"

    result = {
        "trace_id": args.trace_id,
        "expected_trace_id": expected,
        "valid": args.trace_id == expected,
        "checks": {
            "required_fields_present": all(k in payload for k in ["trace_type", "subject", "inputs", "outputs", "steps", "provenance"]),
            "deterministic_id_match": args.trace_id == expected,
        },
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
