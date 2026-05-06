"""Future BS month-length prediction, comparison, and loan-impact services."""

from __future__ import annotations

import csv
import io
import math
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from xml.sax.saxutils import escape

from app.calendar.constants import BS_MAX_YEAR, BS_MIN_YEAR, BS_MONTH_LENGTHS, BS_MONTH_NAMES
from app.calendar.provenance import get_bs_year_provenance

METHOD_VERSION = "parva_future_bs_v1"
CALIBRATION_VERSION = "static_lookup_tail_ensemble_2000_2099_v1"
SUPPORTED_MIN_YEAR = BS_MIN_YEAR
PREDICTION_MAX_YEAR = 2200
MONTH_DAY_VALUES = (29, 30, 31, 32)


@dataclass(frozen=True)
class MonthPrediction:
    month: int
    month_name: str
    final_days: int
    probabilities: dict[str, float]
    confidence_score: float
    confidence_label: str
    risk_flags: list[str]
    model_agreement: str


def _validate_year(bs_year: int) -> None:
    if bs_year < SUPPORTED_MIN_YEAR or bs_year > PREDICTION_MAX_YEAR:
        raise ValueError(
            f"BS year {bs_year} is outside the future-BS engine range "
            f"({SUPPORTED_MIN_YEAR}-{PREDICTION_MAX_YEAR})."
        )


def _validate_month(month: int) -> None:
    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12.")


def _source_label_for_known_year(bs_year: int) -> str:
    provenance = get_bs_year_provenance(bs_year)
    if provenance.confidence == "official":
        return "official_verified"
    if provenance.source_status.startswith("archived_official"):
        return "approved_calendar"
    return "third_party_reference"


def _confidence_label(score: float, *, known_official: bool = False) -> str:
    if known_official:
        return "official_verified"
    if score >= 0.95:
        return "computed_very_high"
    if score >= 0.85:
        return "computed_high"
    if score >= 0.70:
        return "computed_medium"
    if score >= 0.55:
        return "computed_low"
    return "needs_review"


def _prediction_horizon_factor(bs_year: int) -> float:
    if bs_year <= BS_MAX_YEAR:
        return 1.0
    distance = bs_year - BS_MAX_YEAR
    if distance <= 10:
        return 0.94
    if distance <= 25:
        return 0.88
    if distance <= 50:
        return 0.80
    if distance <= 75:
        return 0.72
    return 0.62


def _year_patterns_from_training(end_year: int, window: int = 28) -> list[list[int]]:
    start_year = max(BS_MIN_YEAR, end_year - window + 1)
    return [BS_MONTH_LENGTHS[year] for year in range(start_year, end_year + 1) if year in BS_MONTH_LENGTHS]


def _model_outputs_for_year(bs_year: int) -> dict[str, list[int]]:
    if bs_year in BS_MONTH_LENGTHS:
        known = list(BS_MONTH_LENGTHS[bs_year])
        return {
            "known_corpus_lookup": known,
            "historical_corpus": known,
            "constraint_checked": known,
            "published_static_table": known,
            "source_provenance": known,
        }

    anchor_patterns = _year_patterns_from_training(BS_MAX_YEAR, window=32)
    if not anchor_patterns:
        raise ValueError("No training corpus is available for future BS prediction.")

    offset = bs_year - BS_MAX_YEAR - 1
    last_4 = anchor_patterns[-4:]
    last_12 = anchor_patterns[-12:]
    last_28 = anchor_patterns[-28:]

    outputs: dict[str, list[int]] = {
        "recent_cycle_4": list(last_4[offset % len(last_4)]),
        "recent_cycle_12": list(last_12[offset % len(last_12)]),
        "long_cycle_28": list(last_28[offset % len(last_28)]),
    }

    month_modes: list[int] = []
    for month_index in range(12):
        votes = [pattern[month_index] for pattern in last_28]
        mode, _ = Counter(votes).most_common(1)[0]
        month_modes.append(mode)
    outputs["historical_month_mode"] = month_modes

    weighted_recent: list[int] = []
    for month_index in range(12):
        weighted_votes: Counter[int] = Counter()
        for weight, pattern in enumerate(reversed(last_12), start=1):
            weighted_votes[pattern[month_index]] += weight
        weighted_recent.append(weighted_votes.most_common(1)[0][0])
    outputs["weighted_recent_mode"] = weighted_recent
    return outputs


def _probabilities_from_votes(votes: list[int]) -> dict[str, float]:
    counts = Counter(votes)
    total = len(votes) or 1
    return {f"{days}_days": round(counts.get(days, 0) / total, 4) for days in MONTH_DAY_VALUES}


def _risk_flags(
    *,
    bs_year: int,
    month: int,
    final_days: int,
    max_probability: float,
    vote_counts: Counter[int],
) -> list[str]:
    flags: list[str] = []
    if bs_year > BS_MAX_YEAR:
        flags.append("outside_static_lookup")
    if bs_year > BS_MAX_YEAR + 50:
        flags.append("long_horizon")
    if len(vote_counts) > 1:
        flags.append("model_disagreement")
    if max_probability < 0.70:
        flags.append("manual_review_recommended")
    if final_days not in MONTH_DAY_VALUES:
        flags.append("constraint_violation")
    if month in {5, 8, 11} and max_probability < 0.90:
        flags.append("historically_sensitive_month")
    return flags


def _prediction_rows(bs_year: int) -> list[MonthPrediction]:
    _validate_year(bs_year)
    outputs = _model_outputs_for_year(bs_year)
    known_official = (
        bs_year in BS_MONTH_LENGTHS and get_bs_year_provenance(bs_year).confidence == "official"
    )
    horizon_factor = _prediction_horizon_factor(bs_year)
    source_factor = 1.0 if known_official else (0.92 if bs_year in BS_MONTH_LENGTHS else 0.80)

    predictions: list[MonthPrediction] = []
    model_count = len(outputs)
    for index in range(12):
        votes = [month_lengths[index] for month_lengths in outputs.values()]
        vote_counts = Counter(votes)
        final_days, final_vote_count = vote_counts.most_common(1)[0]
        max_probability = final_vote_count / model_count
        confidence_score = round(max_probability * horizon_factor * source_factor, 4)
        risk_flags = _risk_flags(
            bs_year=bs_year,
            month=index + 1,
            final_days=final_days,
            max_probability=max_probability,
            vote_counts=vote_counts,
        )
        predictions.append(
            MonthPrediction(
                month=index + 1,
                month_name=BS_MONTH_NAMES[index],
                final_days=final_days,
                probabilities=_probabilities_from_votes(votes),
                confidence_score=confidence_score,
                confidence_label=_confidence_label(confidence_score, known_official=known_official),
                risk_flags=risk_flags,
                model_agreement=f"{final_vote_count}/{model_count}",
            )
        )
    return predictions


def _overall_confidence(months: list[MonthPrediction]) -> tuple[float, str]:
    if not months:
        return 0.0, "needs_review"
    score = round(sum(month.confidence_score for month in months) / len(months), 4)
    known_official = all(month.confidence_label == "official_verified" for month in months)
    return score, _confidence_label(score, known_official=known_official)


def _constraint_checks(months: list[int]) -> dict[str, Any]:
    total_days = sum(months)
    valid_month_lengths = all(days in MONTH_DAY_VALUES for days in months)
    plausible_year_total = 354 <= total_days <= 368
    return {
        "valid_month_lengths": valid_month_lengths,
        "year_total_days": total_days,
        "plausible_year_total": plausible_year_total,
        "allowed_month_lengths": list(MONTH_DAY_VALUES),
    }


def predict_bs_year(bs_year: int) -> dict[str, Any]:
    predictions = _prediction_rows(bs_year)
    months = [month.final_days for month in predictions]
    confidence_score, confidence_label = _overall_confidence(predictions)
    provenance = get_bs_year_provenance(bs_year)
    source_type = _source_label_for_known_year(bs_year) if bs_year in BS_MONTH_LENGTHS else "computed_prediction"
    risk_flags = sorted({flag for month in predictions for flag in month.risk_flags})

    return {
        "bs_year": bs_year,
        "months": months,
        "month_details": [
            {
                "month": month.month,
                "month_name": month.month_name,
                "final_days": month.final_days,
                "probability": month.probabilities,
                "confidence_score": month.confidence_score,
                "confidence_label": month.confidence_label,
                "model_agreement": month.model_agreement,
                "risk_flags": month.risk_flags,
            }
            for month in predictions
        ],
        "year_total": sum(months),
        "confidence_score": confidence_score,
        "confidence": confidence_label,
        "risk_flags": risk_flags,
        "constraints": _constraint_checks(months),
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "source": {
            "type": source_type,
            "status": provenance.source_status,
            "structured_official_range": provenance.official_structured_range,
            "static_lookup_range": provenance.static_lookup_range,
            "note": provenance.note,
        },
        "engine_components": [
            "verified_month_length_corpus",
            "civil_month_length_ensemble",
            "constraint_checker",
            "probabilistic_confidence_scoring",
            "loan_contract_risk_adapter",
        ],
        "limits": {
            "known_static_lookup": f"{BS_MIN_YEAR}-{BS_MAX_YEAR} BS",
            "prediction_range": f"{SUPPORTED_MIN_YEAR}-{PREDICTION_MAX_YEAR} BS",
            "ephemeris_status": "swiss_moshier_available; solar-ingress calibration is not yet the authoritative source for v1 outputs",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def predict_bs_range(start: int, end: int) -> dict[str, Any]:
    if start > end:
        raise ValueError("start must be less than or equal to end.")
    if end - start > 200:
        raise ValueError("Range requests are limited to 201 BS years.")
    years = [predict_bs_year(year) for year in range(start, end + 1)]
    return {
        "start": start,
        "end": end,
        "total_years": len(years),
        "years": years,
        "method_version": METHOD_VERSION,
    }


def _external_year_map(years: list[dict[str, Any]]) -> dict[int, list[int]]:
    mapped: dict[int, list[int]] = {}
    for row in years:
        try:
            bs_year = int(row["bs_year"])
            months = [int(value) for value in row["months"]]
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Each external year must include bs_year and 12 numeric months.") from exc
        if len(months) != 12:
            raise ValueError(f"External year {bs_year} must contain exactly 12 month lengths.")
        if any(days not in MONTH_DAY_VALUES for days in months):
            raise ValueError(f"External year {bs_year} contains a month length outside 29-32 days.")
        mapped[bs_year] = months
    return mapped


def compare_external_sheet(source_name: str, years: list[dict[str, Any]]) -> dict[str, Any]:
    external = _external_year_map(years)
    mismatches: list[dict[str, Any]] = []
    matches = 0
    months_compared = 0

    for bs_year, external_months in sorted(external.items()):
        prediction = predict_bs_year(bs_year)
        parva_months = prediction["months"]
        for index, (their_days, parva_days) in enumerate(zip(external_months, parva_months), start=1):
            months_compared += 1
            month_detail = prediction["month_details"][index - 1]
            if their_days == parva_days:
                matches += 1
                continue
            mismatches.append(
                {
                    "bs_year": bs_year,
                    "month": index,
                    "month_name": BS_MONTH_NAMES[index - 1],
                    "their_days": their_days,
                    "parva_days": parva_days,
                    "parva_probability": month_detail["probability"],
                    "confidence": month_detail["confidence_label"],
                    "risk_flags": month_detail["risk_flags"],
                    "recommendation": "manual review before loan or contract use",
                }
            )

    failed = len(mismatches)
    match_rate = round((matches / months_compared) * 100, 2) if months_compared else 0.0
    return {
        "source_name": source_name,
        "summary": {
            "years_compared": len(external),
            "months_compared": months_compared,
            "matches": matches,
            "mismatches": failed,
            "match_rate": match_rate,
        },
        "mismatches": mismatches,
        "method_version": METHOD_VERSION,
    }


def _predict_from_training(bs_year: int, train_start: int, train_end: int) -> list[int]:
    patterns = [BS_MONTH_LENGTHS[year] for year in range(train_start, train_end + 1)]
    if not patterns:
        raise ValueError("Training range has no corpus years.")
    offset = bs_year - train_end - 1
    cycle_pattern = patterns[offset % len(patterns)]
    modes: list[int] = []
    for month_index in range(12):
        votes = [pattern[month_index] for pattern in patterns[-min(28, len(patterns)) :]]
        modes.append(Counter(votes).most_common(1)[0][0])
    blended: list[int] = []
    for month_index in range(12):
        vote_counts = Counter([cycle_pattern[month_index], modes[month_index], patterns[-1][month_index]])
        blended.append(vote_counts.most_common(1)[0][0])
    return blended


def backtest_model(train_start: int, train_end: int, test_start: int, test_end: int) -> dict[str, Any]:
    if train_start > train_end or test_start > test_end:
        raise ValueError("Training and test ranges must be ascending.")
    for year in (train_start, train_end, test_start, test_end):
        if year not in BS_MONTH_LENGTHS:
            raise ValueError(f"Backtest year {year} is outside the static corpus range {BS_MIN_YEAR}-{BS_MAX_YEAR}.")
    if train_end >= test_start:
        raise ValueError("train_end must be earlier than test_start.")

    mismatches: list[dict[str, Any]] = []
    exact_matches = 0
    months_tested = 0
    for year in range(test_start, test_end + 1):
        predicted = _predict_from_training(year, train_start, train_end)
        actual = BS_MONTH_LENGTHS[year]
        for index, (predicted_days, actual_days) in enumerate(zip(predicted, actual), start=1):
            months_tested += 1
            if predicted_days == actual_days:
                exact_matches += 1
            else:
                mismatches.append(
                    {
                        "bs_year": year,
                        "month": index,
                        "month_name": BS_MONTH_NAMES[index - 1],
                        "predicted_days": predicted_days,
                        "actual_days": actual_days,
                    }
                )
    accuracy = round((exact_matches / months_tested) * 100, 2) if months_tested else 0.0
    return {
        "train_range": f"{train_start}-{train_end} BS",
        "test_range": f"{test_start}-{test_end} BS",
        "months_tested": months_tested,
        "exact_matches": exact_matches,
        "mismatches": len(mismatches),
        "accuracy": accuracy,
        "mismatch_details": mismatches,
        "method_version": METHOD_VERSION,
        "calibration_version": CALIBRATION_VERSION,
        "note": "Backtest uses only years withheld from the static corpus and does not certify future official publication.",
    }


def explain_month(year: int, month: int) -> dict[str, Any]:
    _validate_month(month)
    prediction = predict_bs_year(year)
    model_outputs = _model_outputs_for_year(year)
    detail = prediction["month_details"][month - 1]
    return {
        "bs_year": year,
        "month": month,
        "month_name": BS_MONTH_NAMES[month - 1],
        "final_days": detail["final_days"],
        "probability": detail["probability"],
        "confidence": detail["confidence_label"],
        "confidence_score": detail["confidence_score"],
        "model_agreement": detail["model_agreement"],
        "risk_flags": detail["risk_flags"],
        "model_outputs": [
            {"model": name, "days": month_lengths[month - 1]} for name, month_lengths in model_outputs.items()
        ],
        "interpretation": _interpret_month_risk(detail),
        "method_version": METHOD_VERSION,
    }


def _interpret_month_risk(detail: dict[str, Any]) -> str:
    if "manual_review_recommended" in detail["risk_flags"]:
        return "Do not use this month in long-term loan contracts without manual review."
    if "model_disagreement" in detail["risk_flags"]:
        return "Multiple calibrated month-length models disagree; treat as reviewable."
    if detail["confidence_label"] == "official_verified":
        return "Known official structured corpus year."
    return "Prediction is internally consistent under the current v1 ensemble."


def _add_bs_month(year: int, month: int, offset_months: int) -> tuple[int, int]:
    month_zero = (year * 12 + (month - 1)) + offset_months
    return divmod(month_zero, 12)[0], divmod(month_zero, 12)[1] + 1


def simulate_loan_impact(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        start_year_text, start_month_text, _ = str(payload["loan_start_bs"]).split("-")
        start_year = int(start_year_text)
        start_month = int(start_month_text)
        term_months = int(payload["term_months"])
        principal = float(payload["principal"])
        annual_rate = float(payload["annual_rate"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "loan_start_bs, term_months, principal, and annual_rate are required."
        ) from exc

    if term_months <= 0 or term_months > 600:
        raise ValueError("term_months must be between 1 and 600.")
    if principal < 0 or annual_rate < 0:
        raise ValueError("principal and annual_rate must be non-negative.")
    _validate_month(start_month)

    external_years = payload.get("external_years") or []
    external = _external_year_map(external_years) if external_years else {}
    day_count_method = payload.get("day_count_method", "actual_365")
    if day_count_method != "actual_365":
        raise ValueError("Only actual_365 day_count_method is supported in v1.")

    impacted_periods: list[dict[str, Any]] = []
    for installment in range(1, term_months + 1):
        year, month = _add_bs_month(start_year, start_month, installment - 1)
        parva_days = predict_bs_year(year)["months"][month - 1]
        external_days = external.get(year, [None] * 12)[month - 1]
        if external_days is None or external_days == parva_days:
            continue
        day_difference = parva_days - external_days
        interest_difference = principal * (annual_rate / 100.0) * (day_difference / 365.0)
        impacted_periods.append(
            {
                "installment": installment,
                "bs_month": f"{year}-{month:02d}",
                "external_month_days": external_days,
                "parva_month_days": parva_days,
                "day_difference": day_difference,
                "interest_difference_npr": round(interest_difference, 2),
            }
        )

    total_interest_difference = round(sum(row["interest_difference_npr"] for row in impacted_periods), 2)
    max_shift = max((abs(row["day_difference"]) for row in impacted_periods), default=0)
    risk_level = "low"
    if impacted_periods and (abs(total_interest_difference) >= 1000 or max_shift >= 2):
        risk_level = "high"
    elif impacted_periods:
        risk_level = "medium"

    return {
        "summary": {
            "calendar_mismatches_affecting_schedule": len(impacted_periods),
            "first_impacted_installment": impacted_periods[0]["installment"] if impacted_periods else None,
            "max_due_date_shift_days": max_shift,
            "estimated_interest_difference_npr": total_interest_difference,
            "risk_level": risk_level,
        },
        "impacted_periods": impacted_periods,
        "assumptions": {
            "day_count_method": day_count_method,
            "interest_formula": "principal * annual_rate * day_difference / 365",
            "calendar_a": payload.get("calendar_a", "external_sheet"),
            "calendar_b": payload.get("calendar_b", "parva_prediction"),
        },
        "method_version": METHOD_VERSION,
    }


def predictions_to_csv(start: int, end: int) -> str:
    rows = predict_bs_range(start, end)["years"]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "bs_year",
            *[name.lower() for name in BS_MONTH_NAMES],
            "year_total",
            "confidence",
            "method_version",
            "notes",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["bs_year"],
                *row["months"],
                row["year_total"],
                row["confidence"],
                row["method_version"],
                ";".join(row["risk_flags"]) or "none",
            ]
        )
    return buffer.getvalue()


def _excel_cell(column_index: int, row_index: int) -> str:
    letters = ""
    index = column_index
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row_index}"


def _xlsx_sheet_xml(rows: list[list[Any]]) -> str:
    xml_rows: list[str] = []
    for row_index, row in enumerate(rows, start=1):
        cells: list[str] = []
        for column_index, value in enumerate(row, start=1):
            reference = _excel_cell(column_index, row_index)
            if isinstance(value, int | float) and not isinstance(value, bool) and not math.isnan(float(value)):
                cells.append(f'<c r="{reference}"><v>{value}</v></c>')
            else:
                cells.append(
                    f'<c r="{reference}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
                )
        xml_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(xml_rows)}</sheetData>'
        "</worksheet>"
    )


def predictions_to_xlsx(start: int, end: int) -> bytes:
    rows_payload = predict_bs_range(start, end)["years"]
    rows: list[list[Any]] = [
        [
            "bs_year",
            *[name.lower() for name in BS_MONTH_NAMES],
            "year_total",
            "confidence",
            "method_version",
            "notes",
        ]
    ]
    for row in rows_payload:
        rows.append(
            [
                row["bs_year"],
                *row["months"],
                row["year_total"],
                row["confidence"],
                row["method_version"],
                ";".join(row["risk_flags"]) or "none",
            ]
        )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                "</Types>"
            ),
        )
        archive.writestr(
            "_rels/.rels",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                "</Relationships>"
            ),
        )
        archive.writestr(
            "xl/workbook.xml",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                "<sheets><sheet name=\"Future BS\" sheetId=\"1\" r:id=\"rId1\"/></sheets>"
                "</workbook>"
            ),
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                "</Relationships>"
            ),
        )
        archive.writestr("xl/worksheets/sheet1.xml", _xlsx_sheet_xml(rows))
    return buffer.getvalue()
