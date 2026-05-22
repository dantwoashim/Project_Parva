from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE_DIR = ROOT / "conformance" / "public-nepali-date-issues"
DOC_PATHS = [
    ROOT / "docs" / "benchmarks" / "NEPALI_DATE_CONFORMANCE_INDEX.md",
    ROOT / "docs" / "benchmarks" / "PUBLIC_NEPALI_DATE_FAILURE_CLASSES.md",
    ROOT / "docs" / "case-studies" / "yarsa-calendar-source-drift.md",
]

UNSAFE_EXACT_PHRASES = [
    "official " + "truth",
    "Yarsa adopted " + "Project Parva",
    "powers " + "nepal-compliance",
    "official Nepali calendar " + "authority",
    "guaranteed " + "future",
    "cata" + "strophic",
    "infrastructural " + "superiority",
    "must adopt " + "Parva",
]

AUTHORITY_OVERCLAIMS = [
    "government authority",
    "legal authority",
    "tax authority",
    "payroll authority",
    "banking authority",
    "ritual final authority",
]


def _fixture_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in _case_pack_paths())


def _case_pack_paths() -> list[Path]:
    return [
        path
        for path in SUITE_DIR.glob("*.json")
        if path.name != "schema.json"
    ]


def test_public_issue_fixtures_do_not_overclaim_authority() -> None:
    text = _fixture_text()
    for phrase in UNSAFE_EXACT_PHRASES:
        assert phrase not in text

    for path in _case_pack_paths():
        payload = json.loads(path.read_text(encoding="utf-8"))
        for case in payload["cases"]:
            boundary = case["authority_boundary"].lower()
            assert "official" not in boundary or "not official" in boundary
            assert "production impact" not in case["safe_claim"].lower()
            assert "adopted" not in case["safe_claim"].lower()


def test_public_issue_docs_use_bounded_language() -> None:
    for path in DOC_PATHS:
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
        for phrase in UNSAFE_EXACT_PHRASES:
            assert phrase not in text, f"{phrase!r} found in {path}"


def test_public_issue_forbidden_claims_are_negated() -> None:
    for path in _case_pack_paths():
        payload = json.loads(path.read_text(encoding="utf-8"))
        for case in payload["cases"]:
            for claim in case["forbidden_claims"]:
                lowered = claim.lower()
                assert lowered.startswith("do not"), (case["id"], claim)
                for phrase in AUTHORITY_OVERCLAIMS:
                    if phrase in lowered:
                        assert "do not claim" in lowered, (case["id"], claim)
