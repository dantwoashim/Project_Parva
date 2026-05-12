from __future__ import annotations

import json
import shutil
from pathlib import Path

from tools.conformance_runner import run as conformance_run


ROOT = Path(__file__).resolve().parents[2]


def test_public_conformance_suite_passes():
    failures, results = conformance_run.run(ROOT / "conformance")

    assert failures == 0
    assert len(results) >= 20


def test_conformance_runner_fails_on_malformed_case(tmp_path):
    case_root = tmp_path / "conformance"
    shutil.copytree(ROOT / "conformance", case_root)
    case_file = case_root / "conversion" / "bs_to_ad_cases.json"
    payload = json.loads(case_file.read_text(encoding="utf-8"))
    payload["cases"][0].pop("expected")
    case_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    failures, results = conformance_run.run(case_root)

    assert failures == 1
    assert results[0].passed is False
    assert "missing required keys" in results[0].message
