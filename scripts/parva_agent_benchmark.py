#!/usr/bin/env python3
"""Run deterministic public agent benchmark cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.agent_service import (  # noqa: E402
    plan_schedule_payload,
    verify_temporal_claim_payload,
)


def main() -> int:
    cases = [
        ("claim_verified", lambda: verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-14 AD.")["status"] == "verified"),
        ("claim_false", lambda: verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-15 AD.")["status"] == "false"),
        ("claim_unsupported", lambda: verify_temporal_claim_payload("Tell me if this legal contract date is official.")["status"] in {"unsupported", "needs_review"}),
        ("schedule_public", lambda: len(plan_schedule_payload(schedule_type="payroll", bs_year=2082, months=[1])["items"]) == 1),
    ]
    results = []
    for case_id, runner in cases:
        ok = bool(runner())
        results.append({"case_id": case_id, "status": "pass" if ok else "fail"})
    failed = [result for result in results if result["status"] != "pass"]
    report = {
        "benchmark": "agent_temporal_reasoning_public",
        "cases": results,
        "passed": len(results) - len(failed),
        "failed": len(failed),
        "status": "pass" if not failed else "fail",
    }
    print(json.dumps(report, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
