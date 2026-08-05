"""Backtesting for future BS computational and legacy predictors."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.calendar.bikram_sambat import bs_to_gregorian
from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_NAMES

from .accuracy import AccuracyCase, risk_label, source_policy_allows, summarize_accuracy
from .boundary_risk import boundary_risk_label
from .corpus import CorpusRow, corpus_rows, final_test_rows, get_corpus_row
from .legacy_cycle_predictor import predict_from_training
from .models import CALIBRATION_VERSION, METHOD_VERSION
from .solar_ingress_predictor import predict_solar_ingress_year
from .statistical_pattern_predictor import predict_stacked_year
from .unified_predictor import UNIFIED_MODEL_ID, predict_unified_future_bs_year


def _match_count(predicted: list[int], actual: list[int]) -> int:
    return sum(predicted_days == actual_days for predicted_days, actual_days in zip(predicted, actual))


def _validate_backtest_range(train_start: int, train_end: int, test_start: int, test_end: int) -> None:
    if train_start > train_end or test_start > test_end:
        raise ValueError("Training and test ranges must be ascending.")
    for year in (train_start, train_end, test_start, test_end):
        try:
            get_corpus_row(year)
        except ValueError as exc:
            raise ValueError(
                f"Backtest year {year} is outside the static corpus range {BS_MIN_YEAR}-{BS_MAX_YEAR}."
            ) from exc
    if train_end >= test_start:
        raise ValueError("train_end must be earlier than test_start.")


def _rows_for_range(start: int, end: int, source_policy: str) -> list[CorpusRow]:
    rows = [
        row
        for row in corpus_rows()
        if start <= row.bs_year <= end
        and source_policy_allows(row.source_type, row.verification_status, source_policy)
    ]
    if not rows:
        raise ValueError(f"No corpus rows matched {start}-{end} BS with source_policy={source_policy}.")
    return rows


def _parse_agreement(value: str) -> float:
    try:
        numerator, denominator = value.split("/", 1)
        return int(numerator) / int(denominator)
    except (AttributeError, ValueError, ZeroDivisionError):
        return 0.0


def _selected_model_for_month(
    solar: dict[str, Any],
    month_index: int,
    predicted_days: int,
) -> dict[str, Any] | None:
    candidates = [
        model
        for model in solar["model_outputs"]
        if len(model.get("months", [])) > month_index
        and int(model["months"][month_index]) == predicted_days
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda model: float(model.get("rule_weight", 0.0)))


def _month_diagnostics(
    *,
    solar: dict[str, Any],
    month_index: int,
    predicted_days: int,
    actual_days: int,
    row: CorpusRow,
    source_policy: str = "all_reference",
) -> dict[str, Any]:
    selected = _selected_model_for_month(solar, month_index, predicted_days)
    selected_assignment = None
    selected_event = None
    if selected:
        if month_index < len(selected.get("rule_assignments") or []):
            selected_assignment = selected["rule_assignments"][month_index]
        if month_index < len(selected.get("events") or []):
            selected_event = selected["events"][month_index]
    selected_distance = selected_assignment.get("boundary_distance_minutes") if selected_assignment else None
    boundary_distance = selected_distance if isinstance(selected_distance, int) else None
    boundary = boundary_risk_label(boundary_distance)
    risk_flags: set[str] = set()
    if boundary in {"high", "critical"}:
        risk_flags.update(["sankranti_near_civil_assignment_boundary", "manual_review_recommended"])
    month_outputs = [
        int(model["months"][month_index])
        for model in solar["model_outputs"]
        if len(model.get("months", [])) > month_index
    ]
    if len(set(month_outputs)) > 1:
        risk_flags.add("civil_rule_disagreement")
    model_agreement = solar["model_agreement"][month_index]
    probability = solar["probabilities"][month_index]
    confidence_score = max(probability.values()) if probability else 0.0
    agreement_ratio = _parse_agreement(model_agreement)
    label = risk_label(
        confidence_score=confidence_score,
        model_agreement_ratio=agreement_ratio,
        boundary_risk=boundary,
        risk_flags=sorted(risk_flags),
        source_policy=source_policy,
    )
    alternatives = [
        model["model"]
        for model in solar["model_outputs"]
        if len(model.get("months", [])) > month_index
        and int(model["months"][month_index]) == actual_days
    ]
    return {
        "confidence_score": round(confidence_score, 4),
        "model_agreement_ratio": round(agreement_ratio, 4),
        "risk_label": label,
        "boundary_risk": boundary,
        "boundary_distance_minutes": boundary_distance,
        "risk_flags": sorted(risk_flags),
        "predicted_start": (
            selected_assignment.get("assigned_month_start_date") if selected_assignment else None
        ),
        "official_start": bs_to_gregorian(row.bs_year, month_index + 1, 1).isoformat(),
        "ingress_time": selected_event.get("datetime_nepal") if selected_event else None,
        "selected_rule": selected["model"] if selected else None,
        "alternative_rule_that_would_have_worked": alternatives[0] if alternatives else None,
    }


def _stacked_month_diagnostics(
    *,
    stacked: dict[str, Any],
    solar: dict[str, Any],
    month_index: int,
    predicted_days: int,
    actual_days: int,
    row: CorpusRow,
    source_policy: str = "all_reference",
) -> dict[str, Any]:
    diagnostics = _month_diagnostics(
        solar=solar,
        month_index=month_index,
        predicted_days=solar["months"][month_index],
        actual_days=actual_days,
        row=row,
        source_policy=source_policy,
    )
    detail = stacked["month_details"][month_index]
    diagnostics["confidence_score"] = detail["confidence_score"]
    diagnostics["risk_label"] = detail["risk_label"]
    diagnostics["risk_flags"] = sorted(
        set([*diagnostics["risk_flags"], *detail.get("risk_flags", [])])
    )
    if diagnostics["boundary_risk"] in {"high", "critical"}:
        diagnostics["risk_label"] = "RED"
        diagnostics["risk_flags"] = sorted(
            set(
                [
                    *diagnostics["risk_flags"],
                    "sankranti_near_civil_assignment_boundary",
                    "manual_review_recommended",
                ]
            )
        )
    diagnostics["model_agreement_ratio"] = 1.0 if detail.get("model_agreement") == "2/2" else 0.5
    diagnostics["selected_rule"] = detail.get("final_source") or diagnostics["selected_rule"]
    if predicted_days == actual_days:
        diagnostics["alternative_rule_that_would_have_worked"] = detail.get("final_source")
    return diagnostics


def _boundary_bucket(distance: int | None) -> str:
    if distance is None:
        return "unknown"
    if distance < 30:
        return "lt_30_min"
    if distance < 120:
        return "30_to_119_min"
    if distance < 360:
        return "120_to_359_min"
    return "gte_360_min"


def backtest_model(
    train_start: int,
    train_end: int,
    test_start: int,
    test_end: int,
    *,
    source_policy: str = "all_reference",
    training_source_policy: str = "all_reference",
    model: str = "parva_solar_civil_v1",
) -> dict[str, Any]:
    _validate_backtest_range(train_start, train_end, test_start, test_end)

    exact_matches = 0
    exact_year_matches = 0
    legacy_exact_matches = 0
    months_tested = 0
    mismatches: list[dict[str, Any]] = []
    yearly_predictions: list[dict[str, Any]] = []

    accuracy_cases: list[AccuracyCase] = []
    mismatch_by_ingress_hour: Counter[int] = Counter()
    mismatch_by_boundary_distance: Counter[str] = Counter()
    test_rows = _rows_for_range(test_start, test_end, source_policy)
    use_unified_model = model == UNIFIED_MODEL_ID
    use_stacked_model = not use_unified_model and "stack" in model
    effective_training_source_policy = (
        "source_stratified" if use_unified_model else training_source_policy
    )

    for row in test_rows:
        year = row.bs_year
        unified = (
            predict_unified_future_bs_year(
                year,
                train_start=train_start,
                train_end=train_end,
            )
            if use_unified_model
            else None
        )
        stacked = (
            predict_stacked_year(
                year,
                train_start=train_start,
                train_end=train_end,
                source_policy=training_source_policy,
            )
            if use_stacked_model
            else None
        )
        solar = unified or (
            stacked["solar"]
            if stacked
            else predict_solar_ingress_year(
                year,
                train_start=train_start,
                train_end=train_end,
                source_policy=training_source_policy,
            )
        )
        legacy_months, legacy_models = predict_from_training(year, train_start, train_end)
        predicted_months = stacked["months"] if stacked else solar["months"]
        actual = row.months
        solar_matches = _match_count(predicted_months, actual)
        legacy_matches = _match_count(legacy_months, actual)
        exact_matches += solar_matches
        exact_year_matches += int(solar_matches == 12)
        legacy_exact_matches += legacy_matches
        months_tested += 12
        for index, (predicted_days, actual_days) in enumerate(zip(predicted_months, actual), start=1):
            if stacked:
                diagnostics = _stacked_month_diagnostics(
                    stacked=stacked,
                    solar=solar,
                    month_index=index - 1,
                    predicted_days=predicted_days,
                    actual_days=actual_days,
                    row=row,
                    source_policy=source_policy,
                )
            else:
                diagnostics = _month_diagnostics(
                    solar=solar,
                    month_index=index - 1,
                    predicted_days=predicted_days,
                    actual_days=actual_days,
                    row=row,
                    source_policy=source_policy,
                )
            accuracy_cases.append(
                AccuracyCase(
                    bs_year=year,
                    month=index,
                    month_name=BS_MONTH_NAMES[index - 1],
                    predicted_days=predicted_days,
                    actual_days=actual_days,
                    confidence_score=float(diagnostics["confidence_score"]),
                    risk_label=str(diagnostics["risk_label"]),
                    boundary_risk=str(diagnostics["boundary_risk"]),
                    risk_flags=list(diagnostics["risk_flags"]),
                    source_type=row.source_type,
                    verification_status=row.verification_status,
                )
            )
            if predicted_days != actual_days:
                if diagnostics["ingress_time"]:
                    try:
                        hour = int(str(diagnostics["ingress_time"])[11:13])
                        mismatch_by_ingress_hour[hour] += 1
                    except ValueError:
                        pass
                mismatch_by_boundary_distance[_boundary_bucket(diagnostics["boundary_distance_minutes"])] += 1
                mismatches.append(
                    {
                        "bs_year": year,
                        "month": index,
                        "month_name": BS_MONTH_NAMES[index - 1],
                        "predicted_days": predicted_days,
                        "actual_days": actual_days,
                        "predicted_start": diagnostics["predicted_start"],
                        "official_start": diagnostics["official_start"],
                        "ingress_time": diagnostics["ingress_time"],
                        "selected_rule": diagnostics["selected_rule"],
                        "alternative_rule_that_would_have_worked": diagnostics[
                            "alternative_rule_that_would_have_worked"
                        ],
                        "boundary_distance_minutes": diagnostics["boundary_distance_minutes"],
                        "boundary_risk": diagnostics["boundary_risk"],
                        "risk_label": diagnostics["risk_label"],
                        "source_type": row.source_type,
                        "verification_status": row.verification_status,
                    }
                )
        yearly_predictions.append(
            {
                "bs_year": year,
                "predicted": predicted_months,
                "actual": actual,
                "matches": solar_matches,
                "accuracy": round((solar_matches / 12) * 100, 2),
                "source_type": row.source_type,
                "verification_status": row.verification_status,
                "legacy_predicted": legacy_months,
                "legacy_accuracy": round((legacy_matches / 12) * 100, 2),
                "models": [
                    {
                        "model": output["model"],
                        "model_family": "computational_solar_ingress",
                        "rule_weight": output["rule_weight"],
                    }
                    for output in solar["model_outputs"]
                ],
                "legacy_models": legacy_models,
                "stacked_model": stacked["model"] if stacked else None,
                "stacked_statistical": stacked.get("statistical") if stacked else None,
            }
        )

    official_month_cases = len(final_test_rows()) * 12
    accuracy_metrics = summarize_accuracy(accuracy_cases, official_month_cases=official_month_cases)
    return {
        "train_range": f"{train_start}-{train_end} BS",
        "train_start": train_start,
        "train_end": train_end,
        "test_range": f"{test_start}-{test_end} BS",
        "test_start": test_start,
        "test_end": test_end,
        "mode": (
            "authority_aware_unified_rolling_holdout"
            if use_unified_model
            else "solar_statistical_stack_holdout"
            if use_stacked_model
            else "computational_solar_ingress_holdout"
        ),
        "source_policy": source_policy,
        "evaluation_source_policy": source_policy,
        "training_source_policy": effective_training_source_policy,
        "leakage_safe": train_end < test_start,
        "model": model,
        "months_tested": months_tested,
        "exact_matches": exact_matches,
        "exact_year_matches": exact_year_matches,
        "years_tested": len(test_rows),
        "mismatches": len(mismatches),
        "mismatched_months": len(mismatches),
        "accuracy": round((exact_matches / months_tested) * 100, 2) if months_tested else 0.0,
        "month_accuracy": round((exact_matches / months_tested) * 100, 2) if months_tested else 0.0,
        "year_exact_accuracy": round((exact_year_matches / len(test_rows)) * 100, 2) if test_rows else 0.0,
        "overall_top1_accuracy": accuracy_metrics["overall_top1_accuracy"],
        "green_zone_accuracy": accuracy_metrics["green_zone_accuracy"],
        "green_zone_coverage": accuracy_metrics["green_zone_coverage"],
        "boundary_case_accuracy": accuracy_metrics["boundary_case_accuracy"],
        "accuracy_metrics": accuracy_metrics,
        "legacy_exact_matches": legacy_exact_matches,
        "legacy_accuracy": round((legacy_exact_matches / months_tested) * 100, 2) if months_tested else 0.0,
        "yearly_predictions": yearly_predictions,
        "mismatch_details": mismatches,
        "mismatch_by_ingress_hour": dict(sorted(mismatch_by_ingress_hour.items())),
        "mismatch_by_boundary_distance": dict(sorted(mismatch_by_boundary_distance.items())),
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "note": "Solar-ingress backtest is a computational validation aid, not official future publication.",
    }


def full_replay_backtest(
    start: int = BS_MIN_YEAR,
    end: int = BS_MAX_YEAR,
    *,
    source_policy: str = "all_reference",
    training_source_policy: str = "all_reference",
) -> dict[str, Any]:
    if start > end:
        raise ValueError("Backtest range must be ascending.")
    for year in (start, end):
        get_corpus_row(year)
    exact_matches = 0
    months_tested = 0
    years_tested = 0
    exact_year_matches = 0
    mismatch_cases: list[dict[str, Any]] = []
    rows = _rows_for_range(start, end, source_policy)
    for row in rows:
        year = row.bs_year
        solar = predict_solar_ingress_year(
            year,
            train_start=start,
            train_end=end,
            source_policy=training_source_policy,
        )
        actual = row.months
        year_matches = 0
        for index, (predicted_days, actual_days) in enumerate(zip(solar["months"], actual), start=1):
            months_tested += 1
            if predicted_days == actual_days:
                exact_matches += 1
                year_matches += 1
            else:
                mismatch_cases.append(
                    {
                        "bs_year": year,
                        "month": index,
                        "month_name": BS_MONTH_NAMES[index - 1],
                        "official_days": actual_days,
                        "predicted_days": predicted_days,
                        "reason": "civil_assignment_boundary_sensitive",
                        "source_type": row.source_type,
                        "verification_status": row.verification_status,
                    }
                )
        years_tested += 1
        exact_year_matches += int(year_matches == 12)
    return {
        "model_version": METHOD_VERSION,
        "mode": "calibrated_full_replay",
        "source_policy": source_policy,
        "evaluation_source_policy": source_policy,
        "training_source_policy": training_source_policy,
        "leakage_safe": False,
        "evaluation_kind": "in_sample_calibrated_replay_not_forecast_validation",
        "range": f"{start}-{end} BS",
        "months_tested": months_tested,
        "exact_matches": exact_matches,
        "years_tested": years_tested,
        "exact_year_matches": exact_year_matches,
        "mismatches": len(mismatch_cases),
        "mismatched_months": len(mismatch_cases),
        "accuracy": round((exact_matches / months_tested) * 100, 2) if months_tested else 0.0,
        "month_accuracy": round((exact_matches / months_tested) * 100, 2) if months_tested else 0.0,
        "year_exact_accuracy": round((exact_year_matches / years_tested) * 100, 2) if years_tested else 0.0,
        "mismatch_cases": mismatch_cases,
    }


def rolling_validation(
    initial_train_start: int,
    predict_start: int,
    predict_end: int,
    *,
    source_policy: str = "all_reference",
    training_source_policy: str = "all_reference",
    model: str = "parva_solar_civil_v1",
) -> dict[str, Any]:
    if initial_train_start >= predict_start:
        raise ValueError("initial_train_start must be earlier than predict_start.")
    runs: list[dict[str, Any]] = []
    total_matches = 0
    total_months = 0
    total_green_cases = 0
    total_green_passed = 0
    for year in range(predict_start, predict_end + 1):
        run = backtest_model(
            initial_train_start,
            year - 1,
            year,
            year,
            source_policy=source_policy,
            training_source_policy=training_source_policy,
            model=model,
        )
        runs.append(run)
        total_matches += int(run["exact_matches"])
        total_months += int(run["months_tested"])
        metrics = run.get("accuracy_metrics", {})
        total_green_cases += int(metrics.get("green_zone_cases", 0))
        total_green_passed += int(metrics.get("green_zone_passed", 0))
    return {
        "model_version": METHOD_VERSION,
        "mode": "rolling_validation",
        "source_policy": source_policy,
        "evaluation_source_policy": source_policy,
        "training_source_policy": (
            runs[0]["training_source_policy"] if runs else training_source_policy
        ),
        "leakage_safe": all(bool(run.get("leakage_safe")) for run in runs),
        "model": model,
        "initial_train_start": initial_train_start,
        "predict_range": f"{predict_start}-{predict_end} BS",
        "months_tested": total_months,
        "exact_matches": total_matches,
        "accuracy": round((total_matches / total_months) * 100, 2) if total_months else 0.0,
        "month_accuracy": round((total_matches / total_months) * 100, 2) if total_months else 0.0,
        "green_zone_cases": total_green_cases,
        "green_zone_passed": total_green_passed,
        "green_zone_accuracy": (
            round((total_green_passed / total_green_cases) * 100, 2)
            if total_green_cases
            else 0.0
        ),
        "green_zone_coverage": (
            round((total_green_cases / total_months) * 100, 2)
            if total_months
            else 0.0
        ),
        "runs": runs,
    }
