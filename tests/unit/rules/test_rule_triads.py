"""Rule triad integrity tests."""

import pytest

from app.rules import triad_pipeline
from app.rules.catalog_v4 import get_rules_scoreboard


@pytest.fixture(scope="module", autouse=True)
def _generate_triads_once(tmp_path_factory):
    # Keep tests self-contained and avoid writing into tracked data directories.
    original_root = triad_pipeline.TRIAD_ROOT
    triad_pipeline.TRIAD_ROOT = tmp_path_factory.mktemp("rule-triads")
    try:
        triad_pipeline.generate_rule_triads(overwrite=True, computed_only=False)
        yield
    finally:
        triad_pipeline.TRIAD_ROOT = original_root


def test_rule_triads_exist_for_catalog_rows():
    report = triad_pipeline.triad_integrity_report()
    assert report["triad_complete"] == report["total_rules"]
    assert report["triad_missing"] == 0


def test_rule_triads_include_passed_validation_for_computed_baseline():
    report = triad_pipeline.triad_integrity_report()
    scoreboard = get_rules_scoreboard(target=300)
    assert report["rules_with_passed_cases"] >= scoreboard["computed"]["count"]
