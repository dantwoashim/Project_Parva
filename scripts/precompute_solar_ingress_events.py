#!/usr/bin/env python3
"""Precompute solar-ingress events so API requests never solve astronomy live."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.future_bs.ephemeris import JPLDe440Adapter  # noqa: E402
from app.future_bs.solar_ingress_engine import (  # noqa: E402
    _gregorian_sankranti_events,  # noqa: E402
    _jpl_gregorian_sankranti_events,  # noqa: E402
)


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _events_for_year(year: int, ephemeris: str):
    if ephemeris == "jpl_de440":
        adapter = JPLDe440Adapter()
        if not adapter.available:
            raise RuntimeError("PARVA_JPL_DE440_KERNEL must point to a verified DE440 .bsp file.")
        return _jpl_gregorian_sankranti_events(year, adapter)
    if ephemeris == "swiss_moshier":
        return _gregorian_sankranti_events(year, "swiss_moshier_force")
    raise ValueError("ephemeris must be jpl_de440 or swiss_moshier")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1843)
    parser.add_argument("--end", type=int, default=2144)
    parser.add_argument("--ephemeris", choices=["jpl_de440", "swiss_moshier"], default="jpl_de440")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "future_bs" / "astronomy" / "solar_ingress_events_1900_2200.json",
    )
    parser.add_argument("--csv-output", type=Path, default=None)
    parser.add_argument("--parquet-output", type=Path, default=None)
    args = parser.parse_args()

    started = time.perf_counter()
    years: dict[str, list[dict]] = {}
    for year in range(args.start, args.end + 1):
        years[str(year)] = [event.payload() for event in _events_for_year(year, args.ephemeris)]

    payload = {
        "kind": "solar_ingress_events",
        "range": f"{args.start}-{args.end} AD",
        "ephemeris": args.ephemeris,
        "calculation_version": "solar_ingress_solver_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generation_seconds": round(time.perf_counter() - started, 3),
        "years": years,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    csv_output = args.csv_output or args.output.with_suffix(".csv")
    with csv_output.open("w", encoding="utf-8", newline="") as fh:
        fh.write(
            "gregorian_year,bs_month,bs_month_name,rashi_index,rashi_name,"
            "datetime_utc,datetime_nepal,nepal_date,ephemeris,calculation_version\n"
        )
        for year, events in years.items():
            for event in events:
                fh.write(
                    f"{year},{event['bs_month']},{event['bs_month_name']},"
                    f"{event['rashi_index']},{event['rashi_name']},"
                    f"{event['datetime_utc']},{event['datetime_nepal']},"
                    f"{event['nepal_date']},{event['ephemeris']},{event['calculation_version']}\n"
                )
    parquet_output = args.parquet_output or args.output.with_suffix(".parquet")
    parquet_written = False
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq

        records = []
        for year, events in years.items():
            for event in events:
                records.append({"gregorian_year": int(year), **event})
        pq.write_table(pa.Table.from_pylist(records), parquet_output)
        parquet_written = True
    except ImportError:
        parquet_output = None
    print(
        json.dumps(
            {
                "ok": True,
                "output": _display_path(args.output),
                "csv_output": _display_path(csv_output),
                "parquet_output": _display_path(parquet_output) if parquet_output else None,
                "parquet_written": parquet_written,
                "years": len(years),
                "generation_seconds": payload["generation_seconds"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
