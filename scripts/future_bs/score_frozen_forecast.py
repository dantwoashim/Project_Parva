#!/usr/bin/env python3
"""Score a frozen Future BS forecast against later reviewed official truth."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = PROJECT_ROOT / "data" / "future_bs" / "public"
SNAPSHOT_PATH = PUBLIC_DIR / "forecast_snapshot_v7_2084_2200.json"
COMMITMENTS_PATH = PUBLIC_DIR / "frozen" / "v7" / "year_commitments.json"
PROTOCOL_PATH = PUBLIC_DIR / "frozen" / "v7" / "prospective_evaluation_protocol.json"
PUBLICATION_STATUS = "computed_prediction_not_official"
HIGH_SUPPORT_THRESHOLD = 0.8


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_hash(payload: dict[str, Any]) -> str:
    data = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _parse_datetime(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SystemExit(f"{field} must be an ISO-8601 timestamp.") from exc
    if parsed.tzinfo is None:
        raise SystemExit(f"{field} must include a timezone.")
    return parsed


def _validate_source_artifact(truth: dict[str, Any], truth_path: Path) -> None:
    source_sha = str(truth["source_sha256"])
    if not source_sha.startswith("sha256:") or len(source_sha) != 71:
        raise SystemExit("source_sha256 must be a prefixed SHA-256 digest.")
    relative = truth["source_artifact_path"]
    if not isinstance(relative, str) or not relative.strip():
        raise SystemExit("source_artifact_path must identify the reviewed source file.")
    source_path = (truth_path.parent / str(relative)).resolve()
    if not source_path.is_file():
        raise SystemExit(f"Official source artifact is missing: {source_path}")
    actual = "sha256:" + hashlib.sha256(source_path.read_bytes()).hexdigest()
    if actual != source_sha:
        raise SystemExit("Official source artifact hash does not match source_sha256.")


def _validated_truth(path: Path, protocol: dict[str, Any]) -> dict[str, Any]:
    truth = _read_json(path)
    required = protocol["accepted_truth"]["required_fields"]
    missing = [field for field in required if field not in truth]
    if missing:
        raise SystemExit("Official truth is missing fields: " + ", ".join(missing))
    if truth["source_type"] != protocol["accepted_truth"]["required_source_type"]:
        raise SystemExit("Prospective scoring requires source_type=official_verified.")
    source_url = str(truth["source_url"])
    if urlparse(source_url).scheme not in {"http", "https"}:
        raise SystemExit("source_url must be an HTTP or HTTPS URL.")
    if not isinstance(truth["reviewed_by"], list):
        raise SystemExit("reviewed_by must be a list of reviewer identifiers.")
    reviewers = {str(value).strip() for value in truth["reviewed_by"] if str(value).strip()}
    minimum = int(protocol["accepted_truth"]["minimum_independent_reviewers"])
    if len(reviewers) < minimum:
        raise SystemExit(f"Prospective truth requires at least {minimum} independent reviewers.")
    months = [int(value) for value in truth["month_lengths"]]
    if len(months) != 12 or any(value not in {29, 30, 31, 32} for value in months):
        raise SystemExit("Official truth must contain twelve month lengths from 29 through 32.")
    if sum(months) not in {365, 366}:
        raise SystemExit("Official truth must form a 365- or 366-day year.")
    freeze_time = _parse_datetime(protocol["recorded_at"], "freeze recorded_at")
    publication_time = _parse_datetime(str(truth["published_at"]), "published_at")
    if publication_time <= freeze_time:
        raise SystemExit("This source predates the freeze and cannot be scored as prospective truth.")
    retrieval_time = _parse_datetime(str(truth["retrieved_at"]), "retrieved_at")
    if retrieval_time < publication_time:
        raise SystemExit("retrieved_at cannot predate published_at.")
    _validate_source_artifact(truth, path)
    truth["month_lengths"] = months
    truth["reviewed_by"] = sorted(reviewers)
    return truth


def score(truth_path: Path) -> dict[str, Any]:
    snapshot = _read_json(SNAPSHOT_PATH)
    commitments = _read_json(COMMITMENTS_PATH)
    protocol = _read_json(PROTOCOL_PATH)
    truth = _validated_truth(truth_path, protocol)
    bs_year = int(truth["bs_year"])
    forecast = snapshot.get("years", {}).get(str(bs_year))
    if forecast is None:
        raise SystemExit(f"BS {bs_year} is outside the frozen forecast range.")
    commitment = next(
        (entry for entry in commitments["entries"] if int(entry["bs_year"]) == bs_year),
        None,
    )
    if commitment is None:
        raise SystemExit(f"BS {bs_year} has no frozen yearly commitment.")
    leaf = {key: value for key, value in commitment.items() if key != "leaf_sha256"}
    if _canonical_hash(leaf) != commitment["leaf_sha256"]:
        raise SystemExit(f"BS {bs_year} commitment hash is invalid.")
    if (
        snapshot.get("snapshot_id") != commitments.get("snapshot_id")
        or snapshot.get("model_id") != commitments.get("model_id")
        or forecast.get("month_lengths") != commitment.get("month_lengths")
        or forecast.get("year_total_days") != commitment.get("year_total_days")
    ):
        raise SystemExit(f"BS {bs_year} snapshot no longer matches its frozen commitment.")

    predicted = [int(value) for value in forecast["month_lengths"]]
    actual = truth["month_lengths"]
    matches = [left == right for left, right in zip(predicted, actual)]
    wrong_high_support = 0
    month_results: list[dict[str, Any]] = []
    for index, (predicted_days, actual_days) in enumerate(zip(predicted, actual)):
        support = float(
            forecast["months"][index]["model_support"].get(f"{predicted_days}_days", 0.0)
        )
        correct = predicted_days == actual_days
        wrong_high_support += int(not correct and support >= HIGH_SUPPORT_THRESHOLD)
        month_results.append(
            {
                "month": index + 1,
                "predicted_days": predicted_days,
                "official_days": actual_days,
                "correct": correct,
                "selected_model_support": support,
                "absolute_day_error": abs(predicted_days - actual_days),
            }
        )

    exact_matches = sum(matches)
    return {
        "schema": "parva-future-bs-prospective-score-v1",
        "freeze_id": commitments["freeze_id"],
        "model_id": commitments["model_id"],
        "bs_year": bs_year,
        "forecast_leaf_sha256": commitment["leaf_sha256"],
        "truth_source": {
            "source_url": truth["source_url"],
            "source_sha256": truth["source_sha256"],
            "published_at": truth["published_at"],
            "retrieved_at": truth["retrieved_at"],
            "reviewed_by": truth["reviewed_by"],
        },
        "metrics": {
            "exact_month_matches": exact_matches,
            "month_cases": 12,
            "month_accuracy": round(exact_matches / 12, 6),
            "exact_year_match": exact_matches == 12,
            "absolute_day_error": sum(
                abs(predicted_days - actual_days)
                for predicted_days, actual_days in zip(predicted, actual)
            ),
            "wrong_high_support_count": wrong_high_support,
            "high_support_threshold": HIGH_SUPPORT_THRESHOLD,
        },
        "months": month_results,
        "publication_status": PUBLICATION_STATUS,
        "claim_boundary": "One prospectively frozen year is evidence, not a broad guarantee.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--truth", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = score(args.truth.resolve())
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
