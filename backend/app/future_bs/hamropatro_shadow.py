"""HamroPatro shadow-only agreement evaluation.

This module treats HamroPatro as a third-party witness layer. It is deliberately
excluded from official_strict metrics, official claim-readiness, and official
GREEN threshold tuning.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.calendar.constants import BS_MONTH_NAMES

from .legacy_cycle_predictor import predict_legacy_cycle
from .solar_ingress_predictor import predict_solar_ingress_year

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ACCURACY_LAB_DIR = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab"
HAMROPATRO_MONTH_LENGTHS_PATH = (
    PROJECT_ROOT
    / "data"
    / "source_archive"
    / "hamropatro"
    / "hamropatro_month_lengths_2000_2099.json"
)

PUBLICATION_STATUS = "computed_prediction_not_official"
MODE = "hamropatro_shadow_experimental"
SOURCE_POLICY = "third_party_shadow_only_not_official"
EVALUATION_START_YEAR = 2000
EVALUATION_END_YEAR = 2070
SOLAR_CALIBRATION_START = 2078
SOLAR_CALIBRATION_END = 2083


@dataclass(frozen=True)
class ShadowCase:
    bs_year: int
    bs_month: int
    month_name: str
    hamropatro_days: int
    solar_civil_days: int
    legacy_days: int

    @property
    def solar_match(self) -> bool:
        return self.solar_civil_days == self.hamropatro_days

    @property
    def legacy_match(self) -> bool:
        return self.legacy_days == self.hamropatro_days


def _load_hamropatro_years(path: Path | None = None) -> dict[int, list[int]]:
    path = path or HAMROPATRO_MONTH_LENGTHS_PATH
    if not path.exists():
        raise FileNotFoundError(f"Missing HamroPatro source archive: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    years: dict[int, list[int]] = {}
    for row in payload.get("years", []):
        bs_year = int(row["bs_year"])
        months = [int(month["days"]) for month in row["months"]]
        if len(months) == 12:
            years[bs_year] = months
    return years


def _predict_solar_shadow(bs_year: int) -> list[int]:
    return list(
        predict_solar_ingress_year(
            bs_year,
            train_start=SOLAR_CALIBRATION_START,
            train_end=SOLAR_CALIBRATION_END,
            source_policy="official_only",
        )["months"]
    )


def _predict_legacy_shadow(bs_year: int) -> list[int]:
    return list(predict_legacy_cycle(bs_year).months)


def _case_rows(start_year: int, end_year: int, source_path: Path | None = None) -> list[ShadowCase]:
    hamropatro = _load_hamropatro_years(source_path)
    cases: list[ShadowCase] = []
    missing_years = [year for year in range(start_year, end_year + 1) if year not in hamropatro]
    if missing_years:
        raise ValueError(f"HamroPatro source archive missing years: {missing_years}")

    for bs_year in range(start_year, end_year + 1):
        shadow_months = hamropatro[bs_year]
        solar_months = _predict_solar_shadow(bs_year)
        legacy_months = _predict_legacy_shadow(bs_year)
        for month_index, hamropatro_days in enumerate(shadow_months, start=1):
            cases.append(
                ShadowCase(
                    bs_year=bs_year,
                    bs_month=month_index,
                    month_name=BS_MONTH_NAMES[month_index - 1],
                    hamropatro_days=hamropatro_days,
                    solar_civil_days=solar_months[month_index - 1],
                    legacy_days=legacy_months[month_index - 1],
                )
            )
    return cases


def _percent(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _counter_payload(counter: Counter[Any]) -> list[dict[str, Any]]:
    return [
        {"key": key, "count": count}
        for key, count in sorted(counter.items(), key=lambda item: item[0])
    ]


def _mismatches(cases: list[ShadowCase], model: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        predicted = case.solar_civil_days if model == "solar_civil" else case.legacy_days
        if predicted == case.hamropatro_days:
            continue
        rows.append(
            {
                "evaluation_mode": MODE,
                "source_policy": SOURCE_POLICY,
                "model": model,
                "bs_year": case.bs_year,
                "bs_month": case.bs_month,
                "month_name": case.month_name,
                "hamropatro_shadow_days": case.hamropatro_days,
                "predicted_days": predicted,
                "difference": predicted - case.hamropatro_days,
                "is_ashwin_kartik": case.bs_month in {6, 7},
                "involves_29_or_32_day_value": (
                    case.hamropatro_days in {29, 32} or predicted in {29, 32}
                ),
                "official_claim_usable": False,
                "notes": "third-party shadow disagreement; needs official/printed/public-daily verification",
            }
        )
    return rows


def _year_total_anomalies(cases: list[ShadowCase]) -> list[dict[str, Any]]:
    by_year: dict[int, list[ShadowCase]] = defaultdict(list)
    for case in cases:
        by_year[case.bs_year].append(case)
    anomalies: list[dict[str, Any]] = []
    for bs_year, rows in sorted(by_year.items()):
        totals = {
            "hamropatro_shadow_total": sum(row.hamropatro_days for row in rows),
            "solar_civil_total": sum(row.solar_civil_days for row in rows),
            "legacy_total": sum(row.legacy_days for row in rows),
        }
        invalid = {key: value for key, value in totals.items() if value not in {365, 366}}
        if invalid:
            anomalies.append({"bs_year": bs_year, **totals, "invalid_totals": invalid})
    return anomalies


def _clusters(disagreements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    previous_index: int | None = None
    for row in sorted(
        disagreements,
        key=lambda item: (item["model"], int(item["bs_year"]), int(item["bs_month"])),
    ):
        index = (int(row["bs_year"]) * 12) + int(row["bs_month"])
        if current and (
            row["model"] != current[-1]["model"] or previous_index is None or index != previous_index + 1
        ):
            clusters.append(_cluster_payload(current))
            current = []
        current.append(row)
        previous_index = index
    if current:
        clusters.append(_cluster_payload(current))
    return clusters


def _cluster_payload(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "model": rows[0]["model"],
        "start_bs_year": rows[0]["bs_year"],
        "start_bs_month": rows[0]["bs_month"],
        "end_bs_year": rows[-1]["bs_year"],
        "end_bs_month": rows[-1]["bs_month"],
        "count": len(rows),
        "contains_ashwin_kartik": any(row["is_ashwin_kartik"] for row in rows),
        "contains_29_or_32_day_value": any(row["involves_29_or_32_day_value"] for row in rows),
    }


def _verification_queue(
    solar_mismatches: list[dict[str, Any]],
    legacy_mismatches: list[dict[str, Any]],
    limit: int = 100,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], dict[str, Any]] = {}
    for row in [*solar_mismatches, *legacy_mismatches]:
        key = (int(row["bs_year"]), int(row["bs_month"]))
        item = grouped.setdefault(
            key,
            {
                "bs_year": key[0],
                "bs_month": key[1],
                "month_name": row["month_name"],
                "hamropatro_shadow_days": row["hamropatro_shadow_days"],
                "models_disagreeing": [],
                "priority_score": 0,
                "reason": [],
                "official_claim_usable": False,
                "recommended_source_type": "official_verified_or_printed_verified_or_public_daily_witness",
            },
        )
        item["models_disagreeing"].append(row["model"])
        item["priority_score"] += 10
        if row["is_ashwin_kartik"]:
            item["priority_score"] += 8
            item["reason"].append("Ashwin/Kartik boundary month")
        if row["involves_29_or_32_day_value"]:
            item["priority_score"] += 5
            item["reason"].append("29/32-day edge value involved")
    for item in grouped.values():
        models = sorted(set(item["models_disagreeing"]))
        item["models_disagreeing"] = ";".join(models)
        if len(models) > 1:
            item["priority_score"] += 7
            item["reason"].append("both solar-civil and legacy disagree with shadow witness")
        if not item["reason"]:
            item["reason"].append("shadow disagreement")
        item["reason"] = "; ".join(sorted(set(item["reason"])))
    return sorted(
        grouped.values(),
        key=lambda item: (-int(item["priority_score"]), int(item["bs_year"]), int(item["bs_month"])),
    )[:limit]


def evaluate_hamropatro_shadow(
    start_year: int = EVALUATION_START_YEAR,
    end_year: int = EVALUATION_END_YEAR,
    source_path: Path | None = None,
) -> dict[str, Any]:
    cases = _case_rows(start_year, end_year, source_path)
    total = len(cases)
    solar_exact = sum(case.solar_match for case in cases)
    legacy_exact = sum(case.legacy_match for case in cases)
    solar_mismatches = _mismatches(cases, "solar_civil")
    legacy_mismatches = _mismatches(cases, "legacy_static")
    all_mismatches = [*solar_mismatches, *legacy_mismatches]

    mismatches_by_month = Counter(
        f"{row['bs_month']:02d}_{row['month_name']}" for row in all_mismatches
    )
    mismatches_by_year = Counter(int(row["bs_year"]) for row in all_mismatches)
    ashwin_kartik = [row for row in all_mismatches if row["is_ashwin_kartik"]]
    edge_29_32 = [row for row in all_mismatches if row["involves_29_or_32_day_value"]]

    return {
        "publication_status": PUBLICATION_STATUS,
        "evaluation_mode": MODE,
        "source_policy": SOURCE_POLICY,
        "claim_scope": (
            "third-party shadow agreement only; not official accuracy and not official claim-readiness"
        ),
        "source_name": "HamroPatro public daysInMonth JavaScript table archive",
        "source_tier": 6,
        "source_type": "third_party_reference",
        "range": {"start_bs_year": start_year, "end_bs_year": end_year},
        "calibration_policy": {
            "solar_civil_calibration_source_policy": "official_only",
            "solar_civil_calibration_years": [
                SOLAR_CALIBRATION_START,
                SOLAR_CALIBRATION_END,
            ],
            "hamropatro_used_for_calibration": False,
            "hamropatro_used_for_official_strict_metrics": False,
            "hamropatro_used_for_official_claim_readiness": False,
            "hamropatro_used_for_official_green_threshold_tuning": False,
            "hamropatro_supported_rows_marked_official": False,
        },
        "total_months_tested": total,
        "solar_civil_exact_matches": solar_exact,
        "legacy_exact_matches": legacy_exact,
        "solar_civil_shadow_agreement": _percent(solar_exact, total),
        "legacy_shadow_agreement": _percent(legacy_exact, total),
        "solar_civil_mismatch_count": len(solar_mismatches),
        "legacy_mismatch_count": len(legacy_mismatches),
        "mismatches_by_bs_month": _counter_payload(mismatches_by_month),
        "mismatches_by_year": _counter_payload(mismatches_by_year),
        "ashwin_kartik_mismatches": ashwin_kartik,
        "twenty_nine_or_thirty_two_day_mismatches": edge_29_32,
        "year_total_anomalies": _year_total_anomalies(cases),
        "disagreement_clusters": _clusters(all_mismatches),
        "experimental_interpretation": (
            "If solar-civil exceeds legacy/static here, it is experimental shadow evidence only. "
            "It must not be worded as official accuracy."
        ),
        "mismatches": all_mismatches,
        "top_100_rows_needing_verification": _verification_queue(
            solar_mismatches,
            legacy_mismatches,
        ),
    }


def write_hamropatro_shadow_artifacts(
    start_year: int = EVALUATION_START_YEAR,
    end_year: int = EVALUATION_END_YEAR,
    output_dir: Path = ACCURACY_LAB_DIR,
    source_path: Path | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics = evaluate_hamropatro_shadow(start_year, end_year, source_path)
    range_label = f"{start_year}_{end_year}"

    metrics_json = output_dir / f"hamropatro_shadow_{range_label}_metrics.json"
    metrics_md = output_dir / f"hamropatro_shadow_{range_label}_metrics.md"
    disagreements_csv = output_dir / f"hamropatro_shadow_{range_label}_disagreements.csv"
    queue_csv = output_dir / f"hamropatro_shadow_{range_label}_verification_queue.csv"

    metrics_json.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(metrics_md, metrics)
    _write_csv(disagreements_csv, metrics["mismatches"])
    _write_csv(queue_csv, metrics["top_100_rows_needing_verification"])
    return {
        "metrics_json": metrics_json,
        "metrics_md": metrics_md,
        "disagreements_csv": disagreements_csv,
        "verification_queue_csv": queue_csv,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, metrics: dict[str, Any]) -> None:
    lines = [
        (
            "# HamroPatro Shadow Agreement "
            f"{metrics['range']['start_bs_year']}-{metrics['range']['end_bs_year']}"
        ),
        "",
        "This is a third-party shadow agreement report, not official accuracy.",
        "",
        f"- publication_status: `{metrics['publication_status']}`",
        f"- evaluation_mode: `{metrics['evaluation_mode']}`",
        f"- source_policy: `{metrics['source_policy']}`",
        f"- source_tier: `{metrics['source_tier']}`",
        f"- total months tested: {metrics['total_months_tested']}",
        f"- solar_civil_shadow_agreement: {metrics['solar_civil_shadow_agreement']}",
        f"- legacy_shadow_agreement: {metrics['legacy_shadow_agreement']}",
        f"- solar-civil exact matches: {metrics['solar_civil_exact_matches']}",
        f"- legacy/static exact matches: {metrics['legacy_exact_matches']}",
        f"- solar-civil mismatches: {metrics['solar_civil_mismatch_count']}",
        f"- legacy/static mismatches: {metrics['legacy_mismatch_count']}",
        f"- Ashwin/Kartik mismatches: {len(metrics['ashwin_kartik_mismatches'])}",
        f"- 29/32-day mismatches: {len(metrics['twenty_nine_or_thirty_two_day_mismatches'])}",
        f"- year-total anomalies: {len(metrics['year_total_anomalies'])}",
        "",
        "## Guardrails",
        "",
        "- HamroPatro is not used for official_strict metrics.",
        "- HamroPatro is not used for official claim-readiness.",
        "- HamroPatro is not used to tune GREEN thresholds for official claims.",
        "- HamroPatro-supported rows are not marked official.",
        "",
        "## Experimental Interpretation",
        "",
        metrics["experimental_interpretation"],
        "",
        "## Mismatches By BS Month",
        "",
    ]
    for item in metrics["mismatches_by_bs_month"]:
        lines.append(f"- {item['key']}: {item['count']}")
    lines.extend(["", "## Mismatches By Year", ""])
    for item in metrics["mismatches_by_year"]:
        lines.append(f"- {item['key']}: {item['count']}")
    lines.extend(["", "## Top Disagreement Clusters", ""])
    for cluster in metrics["disagreement_clusters"][:20]:
        lines.append(
            "- "
            f"{cluster['model']} "
            f"{cluster['start_bs_year']}-{cluster['start_bs_month']:02d} "
            f"to {cluster['end_bs_year']}-{cluster['end_bs_month']:02d}: "
            f"{cluster['count']} rows"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


__all__ = [
    "MODE",
    "evaluate_hamropatro_shadow",
    "write_hamropatro_shadow_artifacts",
]
