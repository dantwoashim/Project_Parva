from __future__ import annotations

import json
import subprocess
from pathlib import Path

from app.bootstrap.app_factory import create_app
from app.services.protocol_service import (
    issue_calendar_credential_payload,
    protocol_version_payload,
    run_conformance_payload,
    schema_index_payload,
    spec_index_payload,
    verify_calendar_credential_payload,
)
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_protocol_version_specs_and_schemas_exist() -> None:
    assert protocol_version_payload()["protocol_version"] == "parva-protocol-0.1.0"
    assert spec_index_payload()["specs"]
    schema_ids = {schema["schema_id"] for schema in schema_index_payload()["schemas"]}
    assert "calendar-credential.schema" in schema_ids


def test_conformance_runner_passes_core_and_report_has_hash() -> None:
    report = run_conformance_payload(target="local", level="parva_core")
    assert report["status"] == "pass"
    assert report["report_hash"].startswith("sha256:")


def test_calendar_credential_issue_verify_and_tamper_detection() -> None:
    credential = issue_calendar_credential_payload({"claim_type": "date_conversion", "bs_date": "2083-01-01"})["credential"]
    assert verify_calendar_credential_payload(credential)["valid"] is True
    tampered = json.loads(json.dumps(credential))
    tampered["claim"]["object"]["date"] = "2026-04-15"
    assert verify_calendar_credential_payload(tampered)["valid"] is False


def test_protocol_api_endpoints() -> None:
    app = create_app()
    client = TestClient(app)
    assert client.get("/v3/api/protocol/version").status_code == 200
    issue = client.post(
        "/v3/api/protocol/credentials/issue",
        json={"claim_type": "date_conversion", "bs_date": "2083-01-01"},
    )
    assert issue.status_code == 200
    verify = client.post("/v3/api/protocol/credentials/verify", json={"credential": issue.json()["credential"]})
    assert verify.status_code == 200
    assert verify.json()["valid"] is True


def test_offline_bundle_generation_and_verification(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    bundle = subprocess.run(
        ["py", "-3.11", "scripts/parva_offline_bundle.py", "--output", str(output)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert bundle.returncode == 0, bundle.stderr
    verify = subprocess.run(
        ["py", "-3.11", "scripts/parva_offline_verify.py", str(output)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert verify.returncode == 0, verify.stderr
