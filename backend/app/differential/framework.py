"""Differential testing framework for benchmark/result comparisons."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def classify_difference(expected: Any, actual: Any) -> str:
    if expected == actual:
        return "agreement"

    # numeric tolerance classes
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        diff = abs(float(expected) - float(actual))
        if diff <= 1:
            return "minor_difference"
        return "major_difference"

    return "major_difference"


def _classify_observed_maps(
    baseline_observed: Dict[str, Any],
    current_observed: Dict[str, Any],
) -> str:
    if baseline_observed == current_observed:
        return "agreement"

    if not baseline_observed or not current_observed:
        return "incomparable"

    has_major = False
    has_minor = False
    for key, expected in baseline_observed.items():
        if key not in current_observed:
            has_major = True
            continue
        cls = classify_difference(expected, current_observed[key])
        if cls == "major_difference":
            has_major = True
        elif cls == "minor_difference":
            has_minor = True

    if has_major:
        return "major_difference"
    if has_minor:
        return "minor_difference"
    return "agreement"


def _index_results(report: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = report.get("results", [])
    out: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        rid = str(row.get("id"))
        out[rid] = row
    return out


def compare_reports(current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    cur = _index_results(current)
    base = _index_results(baseline)

    compared: List[Dict[str, Any]] = []
    taxonomy_counts = {
        "agreement": 0,
        "minor_difference": 0,
        "major_difference": 0,
        "source_missing": 0,
        "incomparable": 0,
    }

    for rid, row in cur.items():
        if rid not in base:
            taxonomy_counts["source_missing"] += 1
            compared.append({"id": rid, "classification": "source_missing"})
            continue

        cur_observed = row.get("observed", {})
        base_observed = base[rid].get("observed", {})

        if cur_observed and base_observed:
            cls = _classify_observed_maps(base_observed, cur_observed)
            taxonomy_counts[cls] += 1
            compared.append(
                {
                    "id": rid,
                    "classification": cls,
                    "baseline_observed": base_observed,
                    "current_observed": cur_observed,
                }
            )
            continue

        cur_status = row.get("status")
        base_status = base[rid].get("status")
        if cur_status is None or base_status is None:
            taxonomy_counts["incomparable"] += 1
            compared.append({"id": rid, "classification": "incomparable"})
            continue

        cls = classify_difference(base_status, cur_status)
        taxonomy_counts[cls] += 1
        compared.append(
            {
                "id": rid,
                "classification": cls,
                "baseline_status": base_status,
                "current_status": cur_status,
            }
        )

    total = len(compared)
    drift = taxonomy_counts["major_difference"] / total * 100 if total else 0.0

    return {
        "total_compared": total,
        "taxonomy": taxonomy_counts,
        "drift_percent": round(drift, 2),
        "details": compared,
    }


def compare_case_set(current_path: Path, baseline_path: Path) -> Dict[str, Any]:
    current = json.loads(current_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    return compare_reports(current, baseline)
