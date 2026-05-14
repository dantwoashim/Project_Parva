#!/usr/bin/env python3
"""Minimal MCP-style stdio scaffold for Parva public agent-safe tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.agent_service import (  # noqa: E402
    plan_schedule_payload,
    run_tool_payload,
    verify_temporal_claim_payload,
)

MANIFEST_PATH = Path(__file__).with_name("parva_mcp_manifest.json")


def _handle(request: dict[str, object]) -> dict[str, object]:
    method = str(request.get("method") or "")
    params = request.get("params") if isinstance(request.get("params"), dict) else {}
    if method == "manifest":
        return {"ok": True, "manifest": json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))}
    if method == "parva.verify_temporal_claim":
        return {"ok": True, "result": verify_temporal_claim_payload(str(params.get("claim") or ""))}
    if method == "parva.get_fiscal_period":
        return {"ok": True, "result": run_tool_payload("parva.get_fiscal_period", dict(params))}
    if method == "parva.plan_schedule":
        return {
            "ok": True,
            "result": plan_schedule_payload(
                schedule_type="payroll",
                bs_year=int(params.get("bs_year") or 2082),
                months=params.get("months") if isinstance(params.get("months"), list) else [1],
            ),
        }
    return {"ok": False, "error": "unsupported_method"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="store_true", help="Print the local MCP manifest and exit.")
    args = parser.parse_args()
    if args.manifest:
        print(MANIFEST_PATH.read_text(encoding="utf-8"))
        return 0
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            response = _handle(json.loads(line))
        except Exception as exc:  # pragma: no cover - defensive stdio boundary
            response = {"ok": False, "error": type(exc).__name__, "detail": str(exc)}
        print(json.dumps(response, separators=(",", ":")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
