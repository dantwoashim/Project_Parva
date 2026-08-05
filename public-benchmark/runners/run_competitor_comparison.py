#!/usr/bin/env python3
"""Compare public BS conversion packages and replay Parva's forecast window."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = ROOT / "public-benchmark"
COMPETITOR_ROOT = BENCHMARK_ROOT / "competitors"
RESULTS_ROOT = BENCHMARK_ROOT / "results"
GROUND_TRUTH = ROOT / "data" / "future_bs" / "public" / "official_holdout_2078_2083.csv"
OUTPUT_JSON = RESULTS_ROOT / "competitor-comparison.json"
OUTPUT_MD = RESULTS_ROOT / "competitor-comparison.md"
FRONTEND_JSON = ROOT / "frontend" / "src" / "data" / "competitorBenchmark.json"
SNAPSHOT_DATE = "2026-08-05"

BACKEND_ROOT = ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.bikram_sambat import days_in_bs_month  # noqa: E402
from app.research.future_bs.backtest import rolling_validation  # noqa: E402
from app.research.future_bs.unified_predictor import UNIFIED_MODEL_ID  # noqa: E402

MONTH_COLUMNS = [
    "baishakh",
    "jestha",
    "ashadh",
    "shrawan",
    "bhadra",
    "ashwin",
    "kartik",
    "mangsir",
    "poush",
    "magh",
    "falgun",
    "chaitra",
]


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load_ground_truth() -> dict[str, list[int]]:
    with GROUND_TRUTH.open(encoding="utf-8", newline="") as handle:
        rows = csv.DictReader(handle)
        return {
            str(row["bs_year"]): [int(row[column]) for column in MONTH_COLUMNS]
            for row in rows
        }


def _load_node_results() -> dict[str, Any]:
    command = ["node", str(COMPETITOR_ROOT / "run-conversion-conformance.mjs")]
    completed = subprocess.run(
        command,
        cwd=COMPETITOR_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr or completed.stdout or "competitor runner failed")
    return json.loads(completed.stdout)


def _score(
    implementation_id: str,
    version: str,
    source: str,
    years: dict[str, list[int | None]],
    expected: dict[str, list[int]],
    method: str,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    mismatches = []
    exact_matches = 0
    for year, expected_months in expected.items():
        actual_months = years.get(year, [None] * 12)
        for index, expected_days in enumerate(expected_months):
            actual_days = actual_months[index] if index < len(actual_months) else None
            if actual_days == expected_days:
                exact_matches += 1
            else:
                mismatches.append(
                    {
                        "bs_year": int(year),
                        "bs_month": index + 1,
                        "expected_days": expected_days,
                        "actual_days": actual_days,
                    }
                )
    case_count = sum(len(months) for months in expected.values())
    return {
        "implementation": implementation_id,
        "version": version,
        "source": source,
        "method": method,
        "exact_matches": exact_matches,
        "month_cases": case_count,
        "accuracy_percent": round((exact_matches / case_count) * 100, 2),
        "mismatches": mismatches,
        "execution_errors": errors or [],
    }


def _parva_historical(expected: dict[str, list[int]]) -> dict[str, Any]:
    years = {
        year: [days_in_bs_month(int(year), month) for month in range(1, 13)]
        for year in expected
    }
    return _score(
        "Project Parva",
        "repository-main",
        "https://github.com/dantwoashim/Project_Parva",
        years,
        expected,
        "public_days_in_bs_month_api",
    )


def _forecast_replay() -> dict[str, Any]:
    result = rolling_validation(
        2000,
        2078,
        2083,
        source_policy="official_only",
        training_source_policy="source_stratified",
        model=UNIFIED_MODEL_ID,
    )
    return {
        "implementation": "Project Parva future-BS engine",
        "model_id": UNIFIED_MODEL_ID,
        "evaluation_kind": "chronological_rolling_past_only",
        "start_bs_year": 2078,
        "end_bs_year": 2083,
        "exact_matches": result["exact_matches"],
        "month_cases": result["months_tested"],
        "accuracy_percent": result["accuracy"],
        "leakage_safe": result["leakage_safe"],
        "training_source_policy": result["training_source_policy"],
        "year_runs": [
            {
                "test_year": run["test_start"],
                "train_end": run["train_end"],
                "exact_matches": run["exact_matches"],
                "month_cases": run["months_tested"],
            }
            for run in result["runs"]
        ],
        "mismatches": [
            mismatch
            for run in result["runs"]
            for mismatch in run.get("mismatch_details", [])
        ],
    }


def _market_review() -> dict[str, Any]:
    return {
        "as_of": "2026-08-05",
        "match_definition": (
            "A publicly documented Nepal-focused developer API combining BS conversion, "
            "location-aware astronomical Panchanga, Nepal fiscal and working-day rules, "
            "future-BS research, replay artifacts, and a public conformance suite."
        ),
        "conclusion": "No second product matching the full definition was found in the documented review scope.",
        "claim_form": "No equivalent found in our documented market review as of 2026-08-05.",
        "absolute_only_claim_allowed": False,
        "products": [
            {
                "name": "Project Parva",
                "source": "https://github.com/dantwoashim/Project_Parva",
                "nepal_focused": "documented",
                "bs_conversion": "documented",
                "location_aware_astronomical_panchanga": "documented",
                "nepal_business_rules": "documented",
                "future_bs_research": "documented",
                "public_replay_artifacts": "documented",
                "public_conformance_suite": "documented",
            },
            {
                "name": "Prokerala Astrology API",
                "source": "https://api.prokerala.com/",
                "nepal_focused": "not_found_in_review",
                "bs_conversion": "not_found_in_review",
                "location_aware_astronomical_panchanga": "documented",
                "nepal_business_rules": "not_found_in_review",
                "future_bs_research": "not_found_in_review",
                "public_replay_artifacts": "not_found_in_review",
                "public_conformance_suite": "not_found_in_review",
            },
            {
                "name": "TathaAstu API",
                "source": "https://docs.tathaastuapi.com/",
                "nepal_focused": "not_found_in_review",
                "bs_conversion": "not_found_in_review",
                "location_aware_astronomical_panchanga": "documented",
                "nepal_business_rules": "not_found_in_review",
                "future_bs_research": "not_found_in_review",
                "public_replay_artifacts": "not_found_in_review",
                "public_conformance_suite": "not_found_in_review",
            },
            {
                "name": "VedIntel AstroAPI",
                "source": "https://vedintelastroapi.com/docs",
                "nepal_focused": "not_found_in_review",
                "bs_conversion": "not_found_in_review",
                "location_aware_astronomical_panchanga": "documented",
                "nepal_business_rules": "not_found_in_review",
                "future_bs_research": "not_found_in_review",
                "public_replay_artifacts": "not_found_in_review",
                "public_conformance_suite": "not_found_in_review",
            },
            {
                "name": "Nepali date conversion packages",
                "source": "https://www.npmjs.com/search?q=nepali%20date%20converter",
                "nepal_focused": "documented",
                "bs_conversion": "documented",
                "location_aware_astronomical_panchanga": "not_found_in_review",
                "nepal_business_rules": "not_found_in_review",
                "future_bs_research": "not_found_in_review",
                "public_replay_artifacts": "not_found_in_review",
                "public_conformance_suite": "not_found_in_review",
            },
        ],
    }


def _write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Real-Tool Comparison: BS Conformance and Forecast Replay",
        "",
        f"Snapshot: {report['snapshot_date']}",
        "",
        "## Historical BS Month Conformance",
        "",
        "Each implementation was executed through its published BS-to-AD conversion surface. Month length was derived from consecutive month starts and compared with the same 72-case 2078-2083 fixture.",
        "",
        "| Implementation | Version | Exact months | Accuracy |",
        "| --- | --- | ---: | ---: |",
    ]
    for item in report["historical_conformance"]:
        lines.append(
            f"| [{item['implementation']}]({item['source']}) | {item['version']} | "
            f"{item['exact_matches']}/{item['month_cases']} | {item['accuracy_percent']:.2f}% |"
        )
    lines.extend(
        [
            "",
            "Historical conformance measures current lookup/conversion output. It does not test forecasting because every package already contains data for the target years.",
            "",
            "Consumer calendar websites, including Hamro Patro and Nepali Patro, are outside the scored set. This benchmark admits only version-pinned public developer interfaces that can be replayed in CI, and this review did not identify a qualifying interface for either site.",
            "",
            "## Chronological Forecast Replay",
            "",
            f"Parva: {report['forecast_replay']['exact_matches']}/{report['forecast_replay']['month_cases']} exact month predictions ({report['forecast_replay']['accuracy_percent']:.2f}%).",
            "",
            "For each target year, Parva trained only through the previous year. The four conversion packages publish lookup tables rather than forecast methods, so they are not scored in this track.",
            "",
            "## Market Review",
            "",
            report["market_review"]["conclusion"],
            "",
            "The review found other location-aware Panchanga APIs and other Nepali date converters. The defensible distinction is the complete Nepal-focused combination, not an absolute claim that no astronomical Panchanga API exists.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "cd public-benchmark/competitors && npm ci --ignore-scripts",
            "cd ../.. && py -3.11 public-benchmark/runners/run_competitor_comparison.py",
            "```",
            "",
            "The JSON artifact records package versions, per-month mismatches, the forecast replay split, and SHA-256 hashes for the fixture and runners.",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    expected = _load_ground_truth()
    node = _load_node_results()
    historical = [_parva_historical(expected)]
    historical.extend(
        _score(
            item["id"],
            item["version"],
            item["source"],
            item["years"],
            expected,
            item["method"],
            item.get("errors"),
        )
        for item in node["implementations"]
    )
    report = {
        "schema_version": "1.0",
        "snapshot_date": SNAPSHOT_DATE,
        "scope": {
            "bs_year_range": "2078-2083",
            "month_cases": 72,
            "historical_track": "current published conversion output against the common fixture",
            "forecast_track": "Parva chronological past-only replay; lookup-only packages are not scored",
            "admission_rule": "version-pinned public developer interface replayable in CI",
            "excluded_consumer_calendars": ["Hamro Patro", "Nepali Patro"],
            "exclusion_reason": "no qualifying public interface identified in this review; consumer web pages are not scraped",
        },
        "historical_conformance": historical,
        "forecast_replay": _forecast_replay(),
        "market_review": _market_review(),
        "reproducibility": {
            "ground_truth": str(GROUND_TRUTH.relative_to(ROOT)).replace("\\", "/"),
            "ground_truth_sha256": _sha256(GROUND_TRUTH),
            "python_runner_sha256": _sha256(Path(__file__)),
            "node_runner_sha256": _sha256(COMPETITOR_ROOT / "run-conversion-conformance.mjs"),
            "package_lock_sha256": _sha256(COMPETITOR_ROOT / "package-lock.json"),
        },
    }
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FRONTEND_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(report)
    print(json.dumps({
        "ok": True,
        "output": str(OUTPUT_JSON.relative_to(ROOT)),
        "historical": [
            {"implementation": item["implementation"], "score": f"{item['exact_matches']}/{item['month_cases']}"}
            for item in historical
        ],
        "forecast_replay": f"{report['forecast_replay']['exact_matches']}/{report['forecast_replay']['month_cases']}",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
