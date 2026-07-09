#!/usr/bin/env python3
"""Precompute immutable future BS prediction snapshots."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.calendar.constants import BS_MONTH_NAMES  # noqa: E402
from app.research.future_bs.backtest import backtest_model  # noqa: E402
from app.research.future_bs.ensemble import compute_year_live  # noqa: E402
from app.research.future_bs.models import METHOD_VERSION  # noqa: E402
from app.research.future_bs.run_registry import build_run_metadata, write_run_metadata  # noqa: E402


def _compact_prediction(payload: dict) -> dict:
    return payload


def precompute(start: int, end: int, out_dir: Path, *, include_backtest: bool = False) -> dict:
    run = build_run_metadata(start_bs=start, end_bs=end)
    years: dict[str, dict] = {}
    for year in range(start, end + 1):
        prediction = _compact_prediction(compute_year_live(year))
        prediction["run_id"] = run["run_id"]
        prediction["publication_status"] = "not_official_publication"
        years[str(year)] = prediction
    payload = {
        "run_id": run["run_id"],
        "method_version": METHOD_VERSION,
        "start": start,
        "end": end,
        "publication_status": "not_official_publication",
        "years": years,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{METHOD_VERSION}_{start}_{end}.json"
    csv_path = out_dir / f"{METHOD_VERSION}_{start}_{end}.csv"
    backtest_path = out_dir / f"{METHOD_VERSION}_backtest.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(
            [
                "bs_year",
                *[name.lower() for name in BS_MONTH_NAMES],
                "year_total",
                "confidence",
                "method_version",
                "run_id",
                "publication_status",
                "risk_flags",
            ]
        )
        for year in range(start, end + 1):
            row = years[str(year)]
            writer.writerow(
                [
                    year,
                    *row["months"],
                    row["year_total"],
                    row["confidence"],
                    row["method_version"],
                    row["run_id"],
                    row["publication_status"],
                    ";".join(row["risk_flags"]) or "none",
                ]
            )
    if include_backtest:
        try:
            backtest = backtest_model(2040, 2075, 2076, 2083)
        except ValueError as exc:
            backtest = {"error": str(exc)}
        backtest_path.write_text(json.dumps(backtest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_run_metadata(run)
    outputs = {
        "json": str(json_path),
        "csv": str(csv_path),
        "run": str(PROJECT_ROOT / "data" / "future_bs" / "model_runs" / f"{run['run_id']}.json"),
    }
    if include_backtest:
        outputs["backtest"] = str(backtest_path)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=2084)
    parser.add_argument("--end", type=int, default=2200)
    parser.add_argument("--model", default=METHOD_VERSION)
    parser.add_argument("--out-dir", type=Path, default=PROJECT_ROOT / "data" / "future_bs" / "predictions")
    parser.add_argument("--include-backtest", action="store_true")
    args = parser.parse_args()
    if args.model != METHOD_VERSION:
        raise SystemExit(f"Unsupported model {args.model}; expected {METHOD_VERSION}.")
    outputs = precompute(args.start, args.end, args.out_dir, include_backtest=args.include_backtest)
    print(json.dumps(outputs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
