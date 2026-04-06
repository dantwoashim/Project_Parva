#!/usr/bin/env python3
"""Check the public route inventory and compatibility alias coverage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402

SNAPSHOT_PATH = PROJECT_ROOT / "docs" / "contracts" / "v3_route_inventory_snapshot.json"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def _route_rows(prefix: str) -> list[dict[str, object]]:
    schema = app.openapi()
    rows: list[dict[str, object]] = []
    for path, spec in sorted(schema.get("paths", {}).items()):
        if not path.startswith(prefix):
            continue
        methods = sorted(method.upper() for method in spec.keys() if method.lower() in HTTP_METHODS)
        rows.append({"path": path, "methods": methods})
    return rows


def _build_inventory() -> dict[str, object]:
    v3_rows = _route_rows("/v3/api/")
    compat_rows = _route_rows("/api/")

    v3_methods = {
        (row["path"], method)
        for row in v3_rows
        for method in row["methods"]
    }

    alias_gaps: list[dict[str, str]] = []
    for row in compat_rows:
        canonical_path = f"/v3{row['path']}"
        for method in row["methods"]:
            if (canonical_path, method) not in v3_methods:
                alias_gaps.append({"compat_path": row["path"], "canonical_path": canonical_path, "method": method})

    return {
        "schema_version": 1,
        "canonical_prefix": "/v3/api",
        "compat_prefix": "/api",
        "v3_count": len(v3_rows),
        "compat_count": len(compat_rows),
        "alias_gaps": alias_gaps,
        "v3_routes": v3_rows,
        "compat_routes": compat_rows,
    }


def _normalize(payload: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": payload["schema_version"],
        "canonical_prefix": payload["canonical_prefix"],
        "compat_prefix": payload["compat_prefix"],
        "v3_count": payload["v3_count"],
        "compat_count": payload["compat_count"],
        "alias_gaps": payload["alias_gaps"],
        "v3_routes": payload["v3_routes"],
        "compat_routes": payload["compat_routes"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-snapshot", action="store_true", help="Write the current inventory to the frozen snapshot.")
    args = parser.parse_args()

    current = _normalize(_build_inventory())

    if current["alias_gaps"]:
        print("[route-inventory] compatibility routes are missing canonical /v3 counterparts:")
        for gap in current["alias_gaps"]:
            print(f"  - {gap['method']} {gap['compat_path']} -> {gap['canonical_path']}")
        return 1

    if args.write_snapshot:
        SNAPSHOT_PATH.write_text(json.dumps({"inventory": current}, indent=2) + "\n", encoding="utf-8")
        print(f"[route-inventory] wrote snapshot to {SNAPSHOT_PATH}")
        return 0

    if not SNAPSHOT_PATH.exists():
        print(f"[route-inventory] missing snapshot: {SNAPSHOT_PATH}")
        return 2

    frozen = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8")).get("inventory", {})
    if _normalize(frozen) != current:
        print("[route-inventory] current inventory differs from frozen snapshot.")
        return 1

    print("[route-inventory] inventory check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
