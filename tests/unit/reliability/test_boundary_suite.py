from __future__ import annotations

from app.reliability import get_boundary_suite


def test_boundary_suite_has_expected_component_suites():
    payload = get_boundary_suite()

    assert payload["suite_count"] >= 3
    assert payload["total_samples"] >= 80
    ids = {item["suite_id"] for item in payload["suites"]}
    assert {"tithi_boundaries_30", "sankranti_24", "adhik_maas_reference"}.issubset(ids)


def test_boundary_suite_reports_pass_rate_and_samples():
    payload = get_boundary_suite()
    for suite in payload["suites"]:
        assert suite["samples"] >= 1
        assert 0.0 <= suite["pass_rate"] <= 1.0
