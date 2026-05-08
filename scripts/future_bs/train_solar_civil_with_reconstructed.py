#!/usr/bin/env python3
"""Train and evaluate solar-civil rules against reconstructed Tier 1-4 evidence."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.constants import BS_MONTH_LENGTHS, BS_MONTH_NAMES  # noqa: E402
from app.future_bs.models import MONTH_DAY_VALUES  # noqa: E402
from app.future_bs.solar_ingress_predictor import (  # noqa: E402
    REFERENCE_TRAINING_SOURCE_POLICY,
    predict_solar_ingress_year,
    solar_civil_training_summary,
)
from app.future_bs.source_policy import PUBLICATION_STATUS, policy_rows  # noqa: E402

OUT_DIR = PROJECT_ROOT / "data" / "future_bs" / "accuracy_lab"
DEFAULT_JSON = OUT_DIR / "solar_civil_reconstructed_training_report.json"
DEFAULT_MD = OUT_DIR / "solar_civil_reconstructed_training_report.md"
DEFAULT_CSV = OUT_DIR / "solar_civil_reconstructed_mismatches.csv"


def _group_complete_years(policy: str, start: int, end: int) -> dict[int, list[int]]:
    grouped: dict[int, dict[int, int]] = defaultdict(dict)
    for row in policy_rows(policy):
        year = int(row["bs_year"])
        if not start <= year <= end:
            continue
        grouped[year][int(row["bs_month"])] = int(row["month_length"])

    complete: dict[int, list[int]] = {}
    for year, months in grouped.items():
        if len(months) != 12:
            continue
        ordered = [months[month] for month in range(1, 13)]
        if all(value in MONTH_DAY_VALUES for value in ordered) and sum(ordered) in {365, 366}:
            complete[year] = ordered
    return dict(sorted(complete.items()))


def _legacy_months(year: int) -> list[int] | None:
    if year not in BS_MONTH_LENGTHS:
        return None
    return list(BS_MONTH_LENGTHS[year])


def _month_counter() -> dict[str, int]:
    return {str(month): 0 for month in range(1, 13)}


def _evaluate(
    actual_by_year: dict[int, list[int]],
    *,
    train_start: int,
    train_end: int,
    source_policy: str,
    mode: str,
    rolling: bool = False,
) -> dict[str, Any]:
    total = 0
    exact = 0
    mismatches: list[dict[str, Any]] = []
    mismatches_by_month = _month_counter()
    mismatches_by_year: dict[str, int] = {}
    year_total_anomalies: list[dict[str, Any]] = []
    years_evaluated: list[int] = []

    for year, actual in actual_by_year.items():
        effective_train_end = min(train_end, year - 1) if rolling else train_end
        if rolling and effective_train_end < train_start:
            continue
        try:
            predicted = predict_solar_ingress_year(
                year,
                train_start=train_start,
                train_end=effective_train_end,
                source_policy=source_policy,
            )
        except (ValueError, RuntimeError) as exc:
            mismatches.append(
                {
                    "bs_year": year,
                    "bs_month": "",
                    "month_name": "",
                    "actual_days": "",
                    "predicted_days": "",
                    "mode": mode,
                    "error": str(exc),
                }
            )
            continue

        months = predicted["months"]
        years_evaluated.append(year)
        if sum(months) not in {365, 366}:
            year_total_anomalies.append(
                {
                    "bs_year": year,
                    "predicted_total": sum(months),
                    "actual_total": sum(actual),
                    "mode": mode,
                }
            )
        for index, (predicted_days, actual_days) in enumerate(zip(months, actual), start=1):
            total += 1
            if predicted_days == actual_days:
                exact += 1
                continue
            mismatches_by_month[str(index)] += 1
            mismatches_by_year[str(year)] = mismatches_by_year.get(str(year), 0) + 1
            mismatches.append(
                {
                    "bs_year": year,
                    "bs_month": index,
                    "month_name": BS_MONTH_NAMES[index - 1],
                    "actual_days": actual_days,
                    "predicted_days": predicted_days,
                    "mode": mode,
                    "error": "",
                }
            )

    return {
        "mode": mode,
        "source_policy": source_policy,
        "train_start": train_start,
        "train_end": train_end,
        "rolling_pre_publication": rolling,
        "years_evaluated": years_evaluated,
        "year_count": len(years_evaluated),
        "total_months_tested": total,
        "exact_matches": exact,
        "agreement": round(exact / total, 6) if total else 0.0,
        "mismatch_count": total - exact,
        "mismatches_by_month": mismatches_by_month,
        "mismatches_by_year": dict(sorted(mismatches_by_year.items(), key=lambda item: int(item[0]))),
        "ashwin_kartik_mismatches": sum(mismatches_by_month[str(month)] for month in (6, 7)),
        "twenty_nine_or_thirty_two_day_mismatches": sum(
            1
            for mismatch in mismatches
            if mismatch.get("actual_days") in {29, 32} or mismatch.get("predicted_days") in {29, 32}
        ),
        "year_total_anomalies": year_total_anomalies,
        "mismatches": mismatches,
    }


def _evaluate_legacy(actual_by_year: dict[int, list[int]]) -> dict[str, Any]:
    total = 0
    exact = 0
    missing_years: list[int] = []
    mismatches: list[dict[str, Any]] = []
    mismatches_by_month = _month_counter()
    mismatches_by_year: dict[str, int] = {}

    for year, actual in actual_by_year.items():
        predicted = _legacy_months(year)
        if predicted is None:
            missing_years.append(year)
            continue
        for index, (predicted_days, actual_days) in enumerate(zip(predicted, actual), start=1):
            total += 1
            if predicted_days == actual_days:
                exact += 1
                continue
            mismatches_by_month[str(index)] += 1
            mismatches_by_year[str(year)] = mismatches_by_year.get(str(year), 0) + 1
            mismatches.append(
                {
                    "bs_year": year,
                    "bs_month": index,
                    "month_name": BS_MONTH_NAMES[index - 1],
                    "actual_days": actual_days,
                    "predicted_days": predicted_days,
                    "mode": "legacy_static_lookup_against_reconstructed",
                    "error": "",
                }
            )

    return {
        "mode": "legacy_static_lookup_against_reconstructed",
        "total_months_tested": total,
        "exact_matches": exact,
        "agreement": round(exact / total, 6) if total else 0.0,
        "mismatch_count": total - exact,
        "missing_years": missing_years,
        "mismatches_by_month": mismatches_by_month,
        "mismatches_by_year": dict(sorted(mismatches_by_year.items(), key=lambda item: int(item[0]))),
        "mismatches": mismatches,
    }


def _write_mismatches(path: Path, sections: list[dict[str, Any]]) -> None:
    rows: list[dict[str, Any]] = []
    for section in sections:
        rows.extend(section.get("mismatches", []))
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "mode",
        "bs_year",
        "bs_month",
        "month_name",
        "actual_days",
        "predicted_days",
        "error",
    ]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _without_mismatches(section: dict[str, Any]) -> dict[str, Any]:
    clean = dict(section)
    clean.pop("mismatches", None)
    return clean


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    fit = payload["medium_high_solar_civil_calibration_fit"]
    rolling = payload["medium_high_solar_civil_rolling_pre_publication"]
    legacy = payload["legacy_static_against_reconstructed"]
    lines = [
        "# Solar-Civil Reconstructed Training Report",
        "",
        f"Publication status: `{PUBLICATION_STATUS}`",
        "",
        "This is a medium/high-trust reconstructed-corpus calibration report. It is not an official-strict accuracy claim.",
        "",
        "## Training Corpus",
        "",
        f"- Source policy: `{payload['training_source_policy']}`",
        f"- Train range: {payload['train_start']}-{payload['train_end']} BS",
        f"- Reconstructed training rows: {payload['training_summary'].get('reconstructed_training_rows', 0)}",
        f"- Complete usable training years: {payload['training_summary'].get('reconstructed_complete_year_count', 0)}",
        f"- Complete years: {', '.join(str(year) for year in payload['training_summary'].get('reconstructed_complete_years', []))}",
        "",
        "## Agreement Checks",
        "",
        f"- Solar-civil calibration-fit agreement: {fit['exact_matches']}/{fit['total_months_tested']} = {fit['agreement']:.4f}",
        f"- Solar-civil rolling pre-publication agreement: {rolling['exact_matches']}/{rolling['total_months_tested']} = {rolling['agreement']:.4f}",
        f"- Legacy/static agreement against same reconstructed rows: {legacy['exact_matches']}/{legacy['total_months_tested']} = {legacy['agreement']:.4f}",
        "",
        "## Claim Boundary",
        "",
        "- Tier 4 publisher-reference rows are useful for calibration and hard-case discovery.",
        "- They are not official evidence and do not count toward official-strict claim-readiness.",
        "- HamroPatro shadow rows are not used in this training report.",
        "",
        "## Key Diagnostics",
        "",
        f"- Rolling Ashwin/Kartik mismatches: {rolling['ashwin_kartik_mismatches']}",
        f"- Rolling 29/32-day mismatches: {rolling['twenty_nine_or_thirty_two_day_mismatches']}",
        f"- Rolling year-total anomalies: {len(rolling['year_total_anomalies'])}",
        f"- Mismatch CSV: `{payload['mismatch_csv']}`",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def train(
    *,
    source_policy: str,
    start: int,
    end: int,
    out_json: Path,
    out_md: Path,
    out_csv: Path,
) -> dict[str, Any]:
    actual_by_year = _group_complete_years(source_policy, start, end)
    if not actual_by_year:
        raise SystemExit(f"No complete reconstructed years available for {source_policy} {start}-{end}.")

    training_summary = solar_civil_training_summary(
        start,
        end,
        source_policy=source_policy,
    )
    fit = _evaluate(
        actual_by_year,
        train_start=start,
        train_end=end,
        source_policy=source_policy,
        mode="medium_high_solar_civil_calibration_fit",
    )
    rolling = _evaluate(
        actual_by_year,
        train_start=start,
        train_end=end,
        source_policy=source_policy,
        mode="medium_high_solar_civil_rolling_pre_publication",
        rolling=True,
    )
    legacy = _evaluate_legacy(actual_by_year)
    default_policy_fit = _evaluate(
        actual_by_year,
        train_start=start,
        train_end=end,
        source_policy=REFERENCE_TRAINING_SOURCE_POLICY,
        mode="default_all_reference_solar_civil_fit_against_reconstructed",
    )

    _write_mismatches(out_csv, [fit, rolling, legacy, default_policy_fit])

    payload = {
        "publication_status": PUBLICATION_STATUS,
        "report_id": "solar_civil_reconstructed_training_report",
        "training_source_policy": source_policy,
        "train_start": start,
        "train_end": end,
        "official_claim_usable": False,
        "official_claim_note": (
            "This report uses reconstructed Tier 1-4 training evidence and is not official_strict claim-readiness."
        ),
        "hamropatro_used_for_training": False,
        "actual_complete_year_count": len(actual_by_year),
        "actual_complete_years": sorted(actual_by_year),
        "training_summary": training_summary,
        "medium_high_solar_civil_calibration_fit": _without_mismatches(fit),
        "medium_high_solar_civil_rolling_pre_publication": _without_mismatches(rolling),
        "legacy_static_against_reconstructed": _without_mismatches(legacy),
        "default_all_reference_solar_civil_fit_against_reconstructed": _without_mismatches(default_policy_fit),
        "model_selection_note": (
            "Use this trained source policy only as an experimental/non-official calibration candidate unless "
            "official_strict validation and corpus-size gates support promotion."
        ),
        "mismatch_csv": str(out_csv.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(out_md, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-policy", default="medium_high_training")
    parser.add_argument("--start", type=int, default=2050)
    parser.add_argument("--end", type=int, default=2083)
    parser.add_argument("--out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--mismatches", type=Path, default=DEFAULT_CSV)
    args = parser.parse_args()

    payload = train(
        source_policy=args.source_policy,
        start=args.start,
        end=args.end,
        out_json=args.out,
        out_md=args.md,
        out_csv=args.mismatches,
    )
    print(json.dumps({k: v for k, v in payload.items() if k != "training_summary"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
