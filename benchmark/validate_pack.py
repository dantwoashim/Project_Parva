#!/usr/bin/env python3
"""Validate benchmark pack schema for Year-3 standardization prep."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REQUIRED_ROOT = ["pack_id", "version", "description", "calendar_family", "cases"]
REQUIRED_CASE = ["id", "endpoint", "params", "assertions", "source"]


def _error(msg: str, errors: List[str]) -> None:
    errors.append(msg)


def validate_pack_data(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for key in REQUIRED_ROOT:
        if key not in data:
            _error(f"Missing root key: {key}", errors)

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        _error("`cases` must be a non-empty list", errors)
        return errors

    seen_ids = set()
    for idx, case in enumerate(cases):
        if not isinstance(case, dict):
            _error(f"Case #{idx} must be an object", errors)
            continue

        for key in REQUIRED_CASE:
            if key not in case:
                _error(f"Case #{idx} missing key: {key}", errors)

        cid = case.get("id")
        if isinstance(cid, str):
            if cid in seen_ids:
                _error(f"Duplicate case id: {cid}", errors)
            seen_ids.add(cid)

        params = case.get("params")
        if not isinstance(params, dict):
            _error(f"Case {cid or idx}: `params` must be object", errors)

        assertions = case.get("assertions")
        if not isinstance(assertions, dict) or not assertions:
            _error(f"Case {cid or idx}: `assertions` must be non-empty object", errors)

        endpoint = case.get("endpoint")
        if isinstance(endpoint, str) and not endpoint.startswith("/"):
            _error(f"Case {cid or idx}: endpoint must start with '/'", errors)

        tolerance = case.get("tolerance", 0)
        if not isinstance(tolerance, (int, float)):
            _error(f"Case {cid or idx}: tolerance must be numeric", errors)

    return errors


def validate_pack_file(path: Path) -> List[str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"Invalid JSON: {exc}"]

    if not isinstance(payload, dict):
        return ["Pack root must be a JSON object"]

    return validate_pack_data(payload)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: benchmark/validate_pack.py <pack.json>")
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Pack not found: {path}")
        return 2

    errors = validate_pack_file(path)
    if errors:
        print("VALIDATION: FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
