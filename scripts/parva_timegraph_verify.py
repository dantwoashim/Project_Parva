#!/usr/bin/env python3
"""Verify Project Parva public TimeGraph artifacts and queries."""

# ruff: noqa: E402
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.timegraph_service import (
    TimeGraphError,
    bs_ad_fact_id,
    build_public_timegraph,
    get_facts_for_date_payload,
    trace_fact_payload,
    validate_public_timegraph,
)


def main() -> int:
    try:
        graph = build_public_timegraph()
        validation = validate_public_timegraph()
        if not validation["ok"]:
            raise TimeGraphError("; ".join(validation["issues"]))
        sample_fact_id = bs_ad_fact_id(2083, 1, 1)
        trace = trace_fact_payload(sample_fact_id)
        date_query = get_facts_for_date_payload("BS", "2083-01-01")
        if not trace["trace"]["sources"]:
            raise TimeGraphError("sample trace has no sources")
        if not date_query["items"]:
            raise TimeGraphError("sample date query returned no facts")
    except Exception as exc:  # noqa: BLE001
        print(f"Project Parva TimeGraph verification failed: {exc}", file=sys.stderr)
        return 1

    print("Project Parva TimeGraph verification")
    print(
        json.dumps(
            {
                "ok": True,
                "release_id": graph.release_id,
                "fact_count": len(graph.facts),
                "relationship_count": len(graph.relationships),
                "conflict_count": len(graph.conflicts),
                "sample_trace_sources": len(trace["trace"]["sources"]),
                "sample_date_query_items": len(date_query["items"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    print("timegraph verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
