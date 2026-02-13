#!/usr/bin/env python3
"""Run all benchmark packs and generate consolidated baseline summary."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

try:
    from benchmark.harness import run_pack, _build_local_requester
    from benchmark.validate_pack import validate_pack_file
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from harness import run_pack, _build_local_requester  # type: ignore
    from validate_pack import validate_pack_file  # type: ignore

PACK_DIR = Path("benchmark/packs")
RESULT_DIR = Path("benchmark/results")
BASELINE_JSON = RESULT_DIR / "baseline_2028Q1.json"
BASELINE_MD = RESULT_DIR / "baseline_2028Q1.md"


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    requester = _build_local_requester()

    packs = sorted(PACK_DIR.glob("*.json"))
    combined = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_packs": 0,
        "pack_reports": [],
        "summary": {
            "total_cases": 0,
            "passed": 0,
            "failed": 0,
            "avg_pass_rate": 0.0,
        },
    }

    for pack_path in packs:
        errors = validate_pack_file(pack_path)
        if errors:
            raise SystemExit(f"Pack validation failed for {pack_path}: {errors}")

        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        report = run_pack(pack, base_url="http://localhost:8000", requester=requester)

        out_path = RESULT_DIR / f"{pack['pack_id']}_report.json"
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        combined["pack_reports"].append({
            "pack_id": pack["pack_id"],
            "path": str(out_path),
            "summary": report["summary"],
        })

        combined["summary"]["total_cases"] += report["summary"]["total"]
        combined["summary"]["passed"] += report["summary"]["passed"]
        combined["summary"]["failed"] += report["summary"]["failed"]

    combined["total_packs"] = len(combined["pack_reports"])
    if combined["total_packs"]:
        combined["summary"]["avg_pass_rate"] = round(
            sum(p["summary"]["pass_rate"] for p in combined["pack_reports"]) / combined["total_packs"],
            2,
        )

    BASELINE_JSON.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    md = [
        "# Baseline 2028Q1 Benchmark Summary",
        "",
        f"- Generated: `{combined['generated_at']}`",
        f"- Packs: **{combined['total_packs']}**",
        f"- Total cases: **{combined['summary']['total_cases']}**",
        f"- Passed: **{combined['summary']['passed']}**",
        f"- Failed: **{combined['summary']['failed']}**",
        f"- Avg pack pass rate: **{combined['summary']['avg_pass_rate']}%**",
        "",
        "| Pack | Cases | Pass Rate |",
        "|---|---:|---:|",
    ]
    for p in combined["pack_reports"]:
        md.append(f"| {p['pack_id']} | {p['summary']['total']} | {p['summary']['pass_rate']}% |")

    BASELINE_MD.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(combined["summary"], indent=2))
    print(f"Wrote {BASELINE_JSON}")
    print(f"Wrote {BASELINE_MD}")


if __name__ == "__main__":
    main()
