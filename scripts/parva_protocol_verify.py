#!/usr/bin/env python3
"""Verify Parva Protocol public preview artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.protocol_service import (  # noqa: E402
    compatibility_levels_payload,
    issue_calendar_credential_payload,
    offline_bundle_manifest_payload,
    protocol_capabilities_payload,
    protocol_version_payload,
    run_conformance_payload,
    schema_index_payload,
    spec_index_payload,
    verify_calendar_credential_payload,
)


def main() -> int:
    version = protocol_version_payload()
    assert version["protocol_version"] == "parva-protocol-0.1.0"
    assert spec_index_payload()["specs"]
    assert schema_index_payload()["schemas"]
    assert "parva_core" in [level["level"] for level in compatibility_levels_payload()["levels"]]
    report = run_conformance_payload(target="local", level="parva_core")
    assert report["status"] == "pass"
    credential = issue_calendar_credential_payload({"claim_type": "date_conversion", "bs_date": "2083-01-01"})["credential"]
    assert verify_calendar_credential_payload(credential)["valid"] is True
    tampered = json.loads(json.dumps(credential))
    tampered["claim"]["object"]["date"] = "2026-04-15"
    assert verify_calendar_credential_payload(tampered)["valid"] is False
    assert offline_bundle_manifest_payload()["checksums"]
    assert protocol_capabilities_payload()["surface"] == "parva_protocol"
    print("Project Parva protocol verification")
    print(json.dumps({"ok": True, "conformance_tests": report["tests_run"]}, indent=2))
    print("protocol verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
