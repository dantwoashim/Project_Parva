#!/usr/bin/env python3
"""Verify Layer 8 impact simulation behavior."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.impact_service import (  # noqa: E402
    event_schema_payload,
    impact_capabilities_payload,
    recommended_actions_payload,
    semantic_release_diff_payload,
    simulate_change_set_payload,
    simulate_release_diff_payload,
)


def main() -> int:
    capabilities = impact_capabilities_payload()
    assert capabilities["surface"] == "temporal_impact_simulator"
    diff = semantic_release_diff_payload("parva-bs-public-demo", "parva-bs-public-demo")
    assert diff["summary"]["facts_changed"] == 0
    fixture = simulate_release_diff_payload(
        "parva-bs-public-demo",
        "parva-bs-public-demo",
        include_fixture=True,
    )
    assert fixture["summary"]["impacts_found"] >= 1
    assert "REGENERATE_EVIDENCE_PACKET" in fixture["recommendations"] or "RERUN_RULE" in fixture["recommendations"]
    manual = simulate_change_set_payload(
        {
            "change_set_id": "manual_fixture_fact_change",
            "change_set_type": "manual_hypothetical",
            "changes": [
                {
                    "change_type": "FACT_CHANGED",
                    "entity_type": "temporal_fact",
                    "entity_id": "fact_month_length_bs_2082_04",
                    "reason_codes": ["SUPPORTING_FACT_CHANGED"],
                }
            ],
        }
    )
    assert manual["summary"]["changes_analyzed"] == 1
    profile = simulate_change_set_payload(
        {
            "change_set_id": "manual_profile_change",
            "change_set_type": "profile_change",
            "changes": [
                {
                    "change_type": "PROFILE_POLICY_CHANGED",
                    "entity_type": "profile",
                    "entity_id": "nepal_private_company_default",
                    "reason_codes": ["PROFILE_POLICY_CHANGED"],
                }
            ],
        }
    )
    assert profile["summary"]["high"] >= 1
    assert "RERUN_COMPLIANCE_DECISION" in profile["recommendations"]
    assert event_schema_payload()["schema"]["properties"]["signature_status"]
    assert "REGENERATE_EVIDENCE_PACKET" in recommended_actions_payload()["recommended_actions"]
    print("Project Parva impact verification")
    print(json.dumps({"ok": True, "fixture_impacts": fixture["summary"]["impacts_found"]}, indent=2))
    print("impact verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
