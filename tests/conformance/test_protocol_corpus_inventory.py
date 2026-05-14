from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORPUS_ROOT = PROJECT_ROOT / "conformance" / "corpus"
REQUIRED_LEVELS = [
    "source_aware",
    "trust",
    "timegraph",
    "rulelang",
    "impact",
    "agent_safe",
    "offline",
]


def test_phase10_protocol_corpus_has_valid_and_invalid_fixtures() -> None:
    for level in REQUIRED_LEVELS:
        level_dir = CORPUS_ROOT / level
        assert level_dir.exists(), f"missing conformance corpus directory: {level}"
        valid_fixtures = sorted(level_dir.glob("*valid*.json"))
        invalid_fixtures = sorted(level_dir.glob("*invalid*.json"))
        assert valid_fixtures, f"missing valid fixture for {level}"
        assert invalid_fixtures, f"missing invalid fixture for {level}"
        for path in [*valid_fixtures, *invalid_fixtures]:
            payload = json.loads(path.read_text(encoding="utf-8"))
            assert payload["case_id"]
            assert payload["expected"]["status"] in {"pass", "fail"}
