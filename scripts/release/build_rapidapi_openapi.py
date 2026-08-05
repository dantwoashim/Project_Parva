#!/usr/bin/env python3
"""Build the RapidAPI import contract from the canonical public OpenAPI file."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE = PROJECT_ROOT / "docs" / "api-docs" / "openapi.json"
OUTPUT = PROJECT_ROOT / "docs" / "marketplace" / "rapidapi-openapi.json"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}


def main() -> int:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    operation_names: set[str] = set()

    for path, path_item in payload.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            summary = str(operation.get("summary", "")).strip()
            if not summary:
                raise SystemExit(f"RapidAPI endpoint summary missing: {method.upper()} {path}")
            if summary in operation_names:
                raise SystemExit(f"RapidAPI endpoint summary must be unique: {summary}")
            operation_names.add(summary)
            operation["operationId"] = summary

    payload["info"]["title"] = "Project Parva"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(PROJECT_ROOT)} with {len(operation_names)} endpoints.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
