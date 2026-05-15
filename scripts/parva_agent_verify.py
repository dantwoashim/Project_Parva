#!/usr/bin/env python3
"""Verify agent-safe temporal tooling."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.agent_service import (  # noqa: E402
    agent_capabilities_payload,
    agent_manifest_payload,
    agent_tools_payload,
    check_human_review_payload,
    draft_rule_payload,
    plan_schedule_payload,
    resolve_intent_payload,
    run_tool_payload,
    verify_temporal_claim_payload,
)


def main() -> int:
    tools = agent_tools_payload()["tools"]
    assert any(tool["name"] == "parva.verify_temporal_claim" for tool in tools)
    assert agent_capabilities_payload()["surface"] == "agentic_temporal_intelligence"
    assert agent_manifest_payload()["tools"]
    intent = resolve_intent_payload("Does 2083-01-01 BS map to 2026-04-14 AD?")
    assert intent["decision"]["status"] in {"approved", "review_required"}
    verified = verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-14 AD.")
    assert verified["status"] == "verified"
    false_claim = verify_temporal_claim_payload("2083-01-01 BS maps to 2026-04-15 AD.")
    assert false_claim["status"] == "false"
    unsupported = verify_temporal_claim_payload("This complex legal claim is official.")
    assert unsupported["status"] in {"unsupported", "needs_review"}
    schedule = plan_schedule_payload(schedule_type="payroll", bs_year=2082, months=[1, 2])
    assert len(schedule["items"]) == 2
    review = check_human_review_payload({"use_case": "payroll", "confidence": "source_backed"})
    assert review["requires_human_review"] is True
    draft = draft_rule_payload("Move exam dates to the next working day if they fall on a holiday.")
    assert draft["validation"]["valid"] is True
    tool_result = run_tool_payload("parva.verify_temporal_claim", {"claim": "2083-01-01 BS maps to 2026-04-14 AD."})
    assert tool_result["decision"]["status"] == "approved"
    print("Project Parva agent verification")
    print(json.dumps({"ok": True, "tool_count": len(tools), "schedule_items": len(schedule["items"])}, indent=2))
    print("agent verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
