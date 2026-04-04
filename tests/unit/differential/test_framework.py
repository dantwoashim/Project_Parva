from __future__ import annotations

from app.differential import classify_difference, compare_reports


def test_classify_difference_numeric_and_exact():
    assert classify_difference(1, 1) == "agreement"
    assert classify_difference(1, 2) == "minor_difference"
    assert classify_difference(1, 4) == "major_difference"


def test_compare_reports_counts_taxonomy():
    current = {"results": [{"id": "a", "status": "pass"}, {"id": "b", "status": "fail"}]}
    baseline = {"results": [{"id": "a", "status": "pass"}, {"id": "b", "status": "pass"}]}
    out = compare_reports(current, baseline)
    assert out["total_compared"] == 2
    assert out["taxonomy"]["agreement"] == 1
    assert out["taxonomy"]["major_difference"] == 1


def test_compare_reports_prefers_observed_values():
    current = {
        "results": [
            {"id": "a", "status": "pass", "observed": {"bikram_sambat.day": 24}},
            {"id": "b", "status": "pass", "observed": {"tithi.number": 10}},
        ]
    }
    baseline = {
        "results": [
            {"id": "a", "status": "pass", "observed": {"bikram_sambat.day": 24}},
            {"id": "b", "status": "pass", "observed": {"tithi.number": 8}},
        ]
    }
    out = compare_reports(current, baseline)
    assert out["taxonomy"]["agreement"] == 1
    assert out["taxonomy"]["major_difference"] == 1
