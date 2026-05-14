from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENERATED_CORPUS = PROJECT_ROOT / "conformance" / "corpus" / "core" / "generated_public_conversion_220_cases.json"


def test_generated_public_conformance_corpus_has_200_plus_cases() -> None:
    payload = json.loads(GENERATED_CORPUS.read_text(encoding="utf-8"))
    valid_cases = payload["valid_cases"]
    invalid_cases = payload["invalid_cases"]
    assert payload["case_count"] >= 200
    assert len(valid_cases) + len(invalid_cases) == payload["case_count"]
    assert len(valid_cases) >= 150
    assert len(invalid_cases) >= 40
    assert all(case["expected"]["status"] == "pass" for case in valid_cases)
    assert all(case["expected"]["status"] == "fail" for case in invalid_cases)
