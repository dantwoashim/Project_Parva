#!/usr/bin/env python3
"""Build or verify the immutable public commitment for Future BS model v7."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = PROJECT_ROOT / "data" / "future_bs" / "public"
FREEZE_DIR = PUBLIC_DIR / "frozen" / "v7"
SNAPSHOT_PATH = PUBLIC_DIR / "forecast_snapshot_v7_2084_2200.json"
MODEL_PATH = PUBLIC_DIR / "selected_model_v7.json"
COMMITMENTS_PATH = FREEZE_DIR / "year_commitments.json"
PROTOCOL_PATH = FREEZE_DIR / "prospective_evaluation_protocol.json"
TRUTH_SCHEMA_PATH = FREEZE_DIR / "prospective_truth.schema.json"
MANIFEST_PATH = FREEZE_DIR / "freeze_manifest.json"
LEDGER_PATH = PUBLIC_DIR / "forecast_commitment_ledger.jsonl"

FREEZE_ID = "parva_future_bs_v7_2026-08-05"
MODEL_ID = "parva_authority_aware_solar_civil_v7"
SNAPSHOT_ID = "parva_future_bs_public_v7_2084_2200"
SOURCE_COMMIT = "0591ca687b3c91918d1c7557d5033f49d41ba248"
RECORDED_AT = "2026-08-05T10:04:41Z"
TRAINING_CUTOFF = 2083
FIRST_FORECAST_YEAR = 2084
LAST_FORECAST_YEAR = 2200
PUBLICATION_STATUS = "computed_prediction_not_official"

SOURCE_PATHS = (
    "backend/app/research/future_bs/unified_predictor.py",
    "backend/app/research/future_bs/solar_ingress_predictor.py",
    "backend/app/research/future_bs/accuracy_lab.py",
    "backend/app/research/future_bs/backtest.py",
    "backend/app/research/future_bs/corpus.py",
    "backend/app/research/future_bs/models.py",
    "scripts/future_bs/build_public_forecast_snapshot.py",
    "config/ephemeris-kernels.yaml",
    "data/future_bs/public/official_holdout_2078_2083.csv",
    "data/future_bs/public/forecast_snapshot_v7_2084_2200.json",
    "data/future_bs/public/selected_model_v7.json",
)


def _portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _canonical_bytes(payload: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    else:
        text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_record(relative: str) -> dict[str, Any]:
    path = PROJECT_ROOT / relative
    if not path.exists():
        raise SystemExit(f"Freeze source is missing: {relative}")
    payload = _portable_bytes(path)
    return {
        "path": relative,
        "sha256": _sha256_bytes(payload),
        "bytes": len(payload),
    }


def _merkle_root(hashes: list[str]) -> str:
    nodes = [bytes.fromhex(value.removeprefix("sha256:")) for value in hashes]
    if not nodes:
        return _sha256_bytes(b"")
    while len(nodes) > 1:
        if len(nodes) % 2:
            nodes.append(nodes[-1])
        nodes = [
            hashlib.sha256(nodes[index] + nodes[index + 1]).digest()
            for index in range(0, len(nodes), 2)
        ]
    return "sha256:" + nodes[0].hex()


def _validated_sources() -> tuple[dict[str, Any], dict[str, Any]]:
    snapshot = _read_json(SNAPSHOT_PATH)
    model = _read_json(MODEL_PATH)
    if snapshot.get("snapshot_id") != SNAPSHOT_ID:
        raise SystemExit("Unexpected v7 snapshot id.")
    if snapshot.get("model_id") != MODEL_ID or model.get("model_id") != MODEL_ID:
        raise SystemExit("The public snapshot and methodology do not identify model v7.")
    if snapshot.get("publication_status") != PUBLICATION_STATUS:
        raise SystemExit("The frozen snapshot has an unsafe publication status.")
    if int(model.get("training", {}).get("cutoff_bs_year", -1)) != TRAINING_CUTOFF:
        raise SystemExit("The v7 training cutoff is not BS 2083.")
    expected_years = [str(year) for year in range(FIRST_FORECAST_YEAR, LAST_FORECAST_YEAR + 1)]
    if list(snapshot.get("years", {})) != expected_years:
        raise SystemExit("The v7 snapshot does not contain the complete ordered 2084-2200 range.")
    return snapshot, model


def _commitment_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for year in range(FIRST_FORECAST_YEAR, LAST_FORECAST_YEAR + 1):
        forecast = snapshot["years"][str(year)]
        leaf = {
            "bs_year": year,
            "model_id": MODEL_ID,
            "snapshot_id": SNAPSHOT_ID,
            "month_lengths": [int(value) for value in forecast["month_lengths"]],
            "year_total_days": int(forecast["year_total_days"]),
            "publication_status": PUBLICATION_STATUS,
        }
        if len(leaf["month_lengths"]) != 12:
            raise SystemExit(f"BS {year} does not contain twelve month lengths.")
        if sum(leaf["month_lengths"]) != leaf["year_total_days"]:
            raise SystemExit(f"BS {year} has an inconsistent year total.")
        entries.append({**leaf, "leaf_sha256": _sha256_bytes(_canonical_bytes(leaf))})
    root = _merkle_root([entry["leaf_sha256"] for entry in entries])
    return {
        "schema": "parva-future-bs-year-commitments-v1",
        "freeze_id": FREEZE_ID,
        "model_id": MODEL_ID,
        "snapshot_id": SNAPSHOT_ID,
        "recorded_at": RECORDED_AT,
        "source_commit": SOURCE_COMMIT,
        "first_bs_year": FIRST_FORECAST_YEAR,
        "last_bs_year": LAST_FORECAST_YEAR,
        "year_count": len(entries),
        "merkle_algorithm": "duplicate-last-leaf-sha256-pairs",
        "merkle_root": root,
        "entries": entries,
    }


def _evaluation_protocol() -> dict[str, Any]:
    return {
        "schema": "parva-future-bs-prospective-evaluation-v1",
        "freeze_id": FREEZE_ID,
        "model_id": MODEL_ID,
        "recorded_at": RECORDED_AT,
        "development_boundary": {
            "broad_reference_years": "2000-2083 BS",
            "official_rolling_window": "2078-2083 BS",
            "official_month_cases": 72,
            "historical_untouched_test_available": False,
            "reason": (
                "Historical month values through BS 2083 influenced the broad reference tower "
                "or model design and cannot be relabeled as untouched evidence."
            ),
        },
        "prospective_holdout": {
            "primary_bs_year": 2084,
            "additional_locked_years": "2085-2200 BS",
            "truth_status": "awaiting_later_authoritative_publication",
            "forecast_locked_before_truth_import": True,
            "retraining_before_primary_score": False,
        },
        "accepted_truth": {
            "schema_path": str(TRUTH_SCHEMA_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "required_source_type": "official_verified",
            "required_fields": [
                "bs_year",
                "month_lengths",
                "source_type",
                "source_url",
                "source_sha256",
                "source_artifact_path",
                "published_at",
                "retrieved_at",
                "reviewed_by",
            ],
            "minimum_independent_reviewers": 2,
            "publication_must_postdate_freeze": True,
        },
        "locked_metrics": [
            "exact_month_matches",
            "month_accuracy",
            "exact_year_match",
            "absolute_day_error",
            "wrong_high_support_count",
        ],
        "scoring_command": (
            "python scripts/future_bs/score_frozen_forecast.py "
            "--truth <reviewed-official-truth.json>"
        ),
        "claim_boundary": (
            "Prospective scoring begins only after a later authoritative publication is "
            "independently acquired and reviewed."
        ),
    }


def _truth_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://raw.githubusercontent.com/dantwoashim/Project_Parva/main/"
            "data/future_bs/public/frozen/v7/prospective_truth.schema.json"
        ),
        "title": "Project Parva prospective Future BS truth",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "bs_year",
            "month_lengths",
            "source_type",
            "source_url",
            "source_sha256",
            "source_artifact_path",
            "published_at",
            "retrieved_at",
            "reviewed_by",
        ],
        "properties": {
            "bs_year": {
                "type": "integer",
                "minimum": FIRST_FORECAST_YEAR,
                "maximum": LAST_FORECAST_YEAR,
            },
            "month_lengths": {
                "type": "array",
                "minItems": 12,
                "maxItems": 12,
                "items": {"type": "integer", "enum": [29, 30, 31, 32]},
            },
            "source_type": {"const": "official_verified"},
            "source_url": {"type": "string", "format": "uri"},
            "source_sha256": {
                "type": "string",
                "pattern": "^sha256:[0-9a-f]{64}$",
            },
            "source_artifact_path": {"type": "string", "minLength": 1},
            "published_at": {"type": "string", "format": "date-time"},
            "retrieved_at": {"type": "string", "format": "date-time"},
            "reviewed_by": {
                "type": "array",
                "minItems": 2,
                "uniqueItems": True,
                "items": {"type": "string", "minLength": 1},
            },
            "notes": {"type": "string"},
        },
    }


def _ledger_event(commitments: dict[str, Any], snapshot_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "parva-forecast-commitment-ledger-v1",
        "event": "forecast_batch_frozen",
        "freeze_id": FREEZE_ID,
        "recorded_at": RECORDED_AT,
        "source_commit": SOURCE_COMMIT,
        "model_id": MODEL_ID,
        "snapshot_id": SNAPSHOT_ID,
        "training_cutoff_bs_year": TRAINING_CUTOFF,
        "forecast_range": f"{FIRST_FORECAST_YEAR}-{LAST_FORECAST_YEAR} BS",
        "snapshot_sha256": snapshot_record["sha256"],
        "year_commitment_merkle_root": commitments["merkle_root"],
        "publication_status": PUBLICATION_STATUS,
        "signature_status": "unsigned_git_committed_sha256",
    }


def _build_outputs() -> dict[Path, bytes]:
    snapshot, model = _validated_sources()
    commitments = _commitment_payload(snapshot)
    protocol = _evaluation_protocol()
    truth_schema = _truth_schema()
    artifacts = [_artifact_record(relative) for relative in SOURCE_PATHS]
    snapshot_record = next(item for item in artifacts if item["path"] == str(SNAPSHOT_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    ledger_event = _ledger_event(commitments, snapshot_record)
    ledger_event_bytes = _canonical_bytes(ledger_event) + b"\n"
    commitments_bytes = _canonical_bytes(commitments, pretty=True)
    protocol_bytes = _canonical_bytes(protocol, pretty=True)
    truth_schema_bytes = _canonical_bytes(truth_schema, pretty=True)
    manifest = {
        "schema": "parva-future-bs-model-freeze-v1",
        "freeze_id": FREEZE_ID,
        "recorded_at": RECORDED_AT,
        "source_commit": SOURCE_COMMIT,
        "model_id": MODEL_ID,
        "method_version": model["method_version"],
        "calibration_version": model["calibration_version"],
        "snapshot_id": SNAPSHOT_ID,
        "training_cutoff_bs_year": TRAINING_CUTOFF,
        "training_source_policy": "source_stratified",
        "forecast_range": f"{FIRST_FORECAST_YEAR}-{LAST_FORECAST_YEAR} BS",
        "publication_status": PUBLICATION_STATUS,
        "immutability_policy": "Any model or forecast change requires a new version and freeze id.",
        "source_artifacts": artifacts,
        "external_ephemeris_identity": {
            "kernel": "JPL DE440",
            "expected_sha256": "sha256:a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5",
            "binary_committed": False,
        },
        "commitments": {
            "path": str(COMMITMENTS_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "sha256": _sha256_bytes(commitments_bytes),
            "year_merkle_root": commitments["merkle_root"],
        },
        "evaluation_protocol": {
            "path": str(PROTOCOL_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "sha256": _sha256_bytes(protocol_bytes),
        },
        "prospective_truth_schema": {
            "path": str(TRUTH_SCHEMA_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "sha256": _sha256_bytes(truth_schema_bytes),
        },
        "ledger_event": {
            "path": str(LEDGER_PATH.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "sha256": _sha256_bytes(ledger_event_bytes),
        },
        "validation_at_freeze": model["validation"],
        "claim_boundary": (
            "The freeze proves what v7 predicted and which inputs produced it. "
            "It does not prove that unpublished future dates are correct."
        ),
    }
    manifest["manifest_sha256"] = _sha256_bytes(_canonical_bytes(manifest))
    return {
        COMMITMENTS_PATH: commitments_bytes,
        PROTOCOL_PATH: protocol_bytes,
        TRUTH_SCHEMA_PATH: truth_schema_bytes,
        MANIFEST_PATH: _canonical_bytes(manifest, pretty=True),
        LEDGER_PATH: ledger_event_bytes,
    }


def _write(outputs: dict[Path, bytes]) -> None:
    for path, payload in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if path == LEDGER_PATH and path.exists():
            existing = path.read_bytes().replace(b"\r\n", b"\n").splitlines(keepends=True)
            if payload not in existing:
                with path.open("ab") as handle:
                    handle.write(payload)
            continue
        path.write_bytes(payload)


def _check(outputs: dict[Path, bytes]) -> list[str]:
    failures: list[str] = []
    for path, expected in outputs.items():
        relative = path.relative_to(PROJECT_ROOT)
        if not path.exists():
            failures.append(f"missing {relative}")
            continue
        actual = path.read_bytes().replace(b"\r\n", b"\n")
        if path == LEDGER_PATH:
            if expected not in actual.splitlines(keepends=True):
                failures.append(f"missing frozen ledger event in {relative}")
        elif actual != expected:
            failures.append(f"frozen content drifted: {relative}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Write the v7 freeze artifacts")
    mode.add_argument("--check", action="store_true", help="Verify the committed v7 freeze")
    args = parser.parse_args()

    outputs = _build_outputs()
    if args.write:
        _write(outputs)
        print(f"Wrote {FREEZE_ID} with {LAST_FORECAST_YEAR - FIRST_FORECAST_YEAR + 1} committed years.")
        return 0

    failures = _check(outputs)
    if failures:
        for failure in failures:
            print(f"[future-bs-freeze] {failure}")
        return 1
    print(f"Future BS freeze verified: {FREEZE_ID}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
