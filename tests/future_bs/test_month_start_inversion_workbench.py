from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from app.future_bs.month_start.inversion_workbench import (
    PUBLICATION_STATUS,
    build_month_start_inversion_workbench,
    run_month_start_inversion_workbench,
)


@pytest.fixture(scope="module")
def workbench_payload() -> dict:
    return build_month_start_inversion_workbench(max_year=2083)


def test_workbench_builds_required_sections_without_future_rows(workbench_payload: dict) -> None:
    payload = workbench_payload

    assert payload["publication_status"] == PUBLICATION_STATUS
    assert payload["historical_only"] is True
    for key in (
        "month_start_candidates",
        "solar_ingress_timing_features",
        "civil_date_assignment_candidates",
        "official_match_labels",
        "boundary_risk_cases",
        "rule_inversion_summary",
        "false_green_memory",
        "top_verification_targets",
    ):
        assert key in payload

    assert payload["rule_inversion_summary"]["official_label_months"] == 72
    assert payload["rule_inversion_summary"]["official_label_years"] == [
        2078,
        2079,
        2080,
        2081,
        2082,
        2083,
    ]
    assert all(
        int(row["bs_year"]) <= 2083
        for section in (
            "month_start_candidates",
            "solar_ingress_timing_features",
            "civil_date_assignment_candidates",
            "official_match_labels",
            "boundary_risk_cases",
            "false_green_memory",
            "top_verification_targets",
        )
        for row in payload[section]
    )


def test_official_labels_have_one_case_per_rule_and_no_future_shadow_leakage(workbench_payload: dict) -> None:
    payload = workbench_payload
    labels = payload["official_match_labels"]
    by_rule: dict[str, int] = {}
    for row in labels:
        by_rule[row["rule_name"]] = by_rule.get(row["rule_name"], 0) + 1
        assert row["source_type"] == "official_verified"
        assert row["verification_status"] == "verified"
        assert row["leakage_policy"] != "future_shadow_reference"
        assert row["official_match"] in {"true", "false"}
        assert row["candidate_month_start_ad"]
        assert row["official_month_start_ad"]

    assert by_rule
    assert all(count == 72 for count in by_rule.values())


def test_rule_inversion_summary_keeps_diagnostic_claim_boundary(workbench_payload: dict) -> None:
    payload = workbench_payload
    summary = payload["rule_inversion_summary"]

    assert summary["publication_status"] == PUBLICATION_STATUS
    assert summary["corpus_bottleneck"]["status"] == "underpowered"
    assert summary["corpus_bottleneck"]["minimum_recommended_for_strong_inversion"] == 150
    assert "official future dates" in summary["claim_boundary"]
    assert all(row["claim_use"] == "diagnostic_only" for row in summary["rule_scores"])
    assert set(summary["effective_cutoff_surfaces"]) == {str(month) for month in range(1, 13)}


def test_workbench_writes_all_artifacts(tmp_path) -> None:
    result = run_month_start_inversion_workbench(output_dir=tmp_path, max_year=2083)

    paths = result["artifacts"]
    assert paths
    for path in paths.values():
        artifact = Path(path)
        assert artifact.exists()
        assert artifact.stat().st_size > 0

    summary = json.loads((tmp_path / "rule_inversion_summary.json").read_text(encoding="utf-8"))
    assert summary["official_label_months"] == 72

    with (tmp_path / "official_match_labels.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows
    assert {row["publication_status"] for row in rows if "publication_status" in row} in (
        set(),
        {PUBLICATION_STATUS},
    )


def test_verification_targets_prioritize_non_official_historical_rows() -> None:
    payload = build_month_start_inversion_workbench(max_year=2083, top_target_limit=25)
    targets = payload["top_verification_targets"]

    assert 0 < len(targets) <= 25
    assert all(row["current_source_type"] != "official_verified" for row in targets)
    assert all(int(row["bs_year"]) <= 2083 for row in targets)
    assert all(row["recommended_manual_action"] for row in targets)
    assert targets == sorted(
        targets,
        key=lambda row: (-int(row["priority"]), int(row["bs_year"]), int(row["bs_month"])),
    )
