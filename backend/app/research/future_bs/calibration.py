"""Calibration summaries for future BS model families."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from app.calendar.bikram_sambat import bs_to_gregorian
from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR
from app.research.future_bs.paths import project_root

from .accuracy import source_policy_allows
from .corpus import corpus_rows
from .solar_ingress_engine import events_around_bs_year
from .solar_ingress_predictor import calibrated_rule_weights

PROJECT_ROOT = project_root()
CALIBRATION_DIR = PROJECT_ROOT / "data" / "future_bs" / "calibration"


def civil_decision_samples(
    train_start: int = BS_MIN_YEAR,
    train_end: int = BS_MAX_YEAR,
    *,
    source_policy: str = "train_allowed",
) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    eligible_rows = [
        row
        for row in corpus_rows()
        if train_start <= row.bs_year <= train_end
        and source_policy_allows(row.source_type, row.verification_status, source_policy)
    ]
    for row in eligible_rows:
        events = events_around_bs_year(row.bs_year)
        for month in range(1, 13):
            official_start = bs_to_gregorian(row.bs_year, month, 1)
            candidates = [event for event in events if event.bs_month == month]
            if not candidates:
                continue
            event = min(
                candidates,
                key=lambda candidate: abs((candidate.datetime_nepal.date() - official_start).days),
            )
            decision_days = (official_start - event.datetime_nepal.date()).days
            minute_of_day = event.datetime_nepal.hour * 60 + event.datetime_nepal.minute
            samples.append(
                {
                    "bs_year": row.bs_year,
                    "bs_month": month,
                    "minute_of_day": minute_of_day,
                    "ingress_nepal_time": event.datetime_nepal.isoformat(),
                    "official_start": official_start.isoformat(),
                    "decision_days": decision_days,
                    "source_type": row.source_type,
                    "verification_status": row.verification_status,
                }
            )
    return samples


def _cutoff_to_text(cutoff: int) -> str:
    return f"{cutoff // 60:02d}:{cutoff % 60:02d}"


def calibrate_month_cutoffs(
    train_start: int = BS_MIN_YEAR,
    train_end: int = BS_MAX_YEAR,
    *,
    source_policy: str = "train_allowed",
) -> dict[str, Any]:
    samples = civil_decision_samples(train_start, train_end, source_policy=source_policy)
    by_month: dict[int, list[dict[str, Any]]] = defaultdict(list)
    excluded = 0
    for sample in samples:
        if sample["decision_days"] not in {0, 1}:
            excluded += 1
            continue
        by_month[int(sample["bs_month"])].append(sample)

    month_results: list[dict[str, Any]] = []
    total = 0
    correct = 0
    for month in range(1, 13):
        rows = by_month.get(month, [])
        best_cutoff = 720
        best_errors = len(rows)
        for cutoff in range(24 * 60):
            errors = sum(
                (0 if int(row["minute_of_day"]) <= cutoff else 1) != int(row["decision_days"])
                for row in rows
            )
            if errors < best_errors or (errors == best_errors and abs(cutoff - 720) < abs(best_cutoff - 720)):
                best_cutoff = cutoff
                best_errors = errors
        tested = len(rows)
        matches = tested - best_errors
        total += tested
        correct += matches
        month_results.append(
            {
                "month": month,
                "cutoff_minutes": best_cutoff,
                "cutoff": _cutoff_to_text(best_cutoff),
                "samples": tested,
                "matches": matches,
                "errors": best_errors,
                "decision_accuracy": round((matches / tested) * 100, 2) if tested else 0.0,
            }
        )

    return {
        "calibration": "month_specific_cutoff_grid_search",
        "train_range": f"{train_start}-{train_end} BS",
        "source_policy": source_policy,
        "samples": len(samples),
        "usable_samples": total,
        "excluded_non_binary_decisions": excluded,
        "overall_decision_accuracy": round((correct / total) * 100, 2) if total else 0.0,
        "month_cutoffs": month_results,
    }


def write_calibration_artifacts(
    train_start: int = BS_MIN_YEAR,
    train_end: int = BS_MAX_YEAR,
    *,
    source_policy: str = "train_allowed",
) -> dict[str, str]:
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
    civil_rules = calibrate_month_cutoffs(train_start, train_end, source_policy=source_policy)
    labels = civil_decision_samples(train_start, train_end, source_policy=source_policy)
    ayanamsha = {
        "status": "registered_for_nested_validation",
        "active": "lahiri",
        "candidates": ["lahiri", "raman", "krishnamurti", "fagan_bradley", "calibrated_offset"],
        "note": "Do not select a non-Lahiri production model until nested validation has enough official/printed samples.",
    }
    final_selected = {
        "model": "solar_civil_ensemble_v4",
        "source_policy": source_policy,
        "civil_rule_family": "month_specific_cutoff_grid_search_with_boundary_abstention",
        "claim_boundary": "Selected as evaluation model only; not a 99% claim.",
        "civil_rule_results": civil_rules,
        "ayanamsha": ayanamsha,
    }
    paths = {
        "civil_rule_training_labels": str(CALIBRATION_DIR / "civil_rule_training_labels.json"),
        "civil_rule_results": str(CALIBRATION_DIR / "civil_rule_results.json"),
        "ayanamsha_results": str(CALIBRATION_DIR / "ayanamsha_results.json"),
        "final_selected_model": str(CALIBRATION_DIR / "final_selected_model.json"),
    }
    (CALIBRATION_DIR / "civil_rule_training_labels.json").write_text(
        json.dumps(labels, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (CALIBRATION_DIR / "civil_rule_results.json").write_text(
        json.dumps(civil_rules, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (CALIBRATION_DIR / "ayanamsha_results.json").write_text(
        json.dumps(ayanamsha, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (CALIBRATION_DIR / "final_selected_model.json").write_text(
        json.dumps(final_selected, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return paths


def calibration_summary(train_start: int = BS_MIN_YEAR, train_end: int = BS_MAX_YEAR) -> dict[str, Any]:
    weights = calibrated_rule_weights(train_start, train_end)
    cutoffs = calibrate_month_cutoffs(train_start, train_end, source_policy="train_allowed")
    return {
        "train_range": f"{train_start}-{train_end} BS",
        "rule_weights_percent": {name: round(weight * 100, 2) for name, weight in weights.items()},
        "civil_rule_grid_search": cutoffs,
        "selected_family": "solar_ingress_civil_rule_ensemble",
        "status": "calibrated_against_source_labeled_corpus",
    }
