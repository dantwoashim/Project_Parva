#!/usr/bin/env python3
"""Generate monthly scorecard and track evaluation trend history."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVAL = PROJECT_ROOT / "reports" / "evaluation_v4" / "evaluation_v4.json"
HISTORY_PATH = PROJECT_ROOT / "reports" / "evaluation_history.jsonl"
OUT_MD = PROJECT_ROOT / "reports" / "evaluation_scorecard.md"


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate evaluation scorecard")
    parser.add_argument("--evaluation-json", default=str(DEFAULT_EVAL), help="Path to evaluation_v4.json")
    parser.add_argument("--history", default=str(HISTORY_PATH), help="Path to trend history jsonl")
    parser.add_argument("--output", default=str(OUT_MD), help="Scorecard markdown output")
    parser.add_argument("--label", default=datetime.utcnow().strftime("%Y-%m-%d"), help="Run label")
    args = parser.parse_args()

    eval_path = Path(args.evaluation_json)
    history_path = Path(args.history)
    output_path = Path(args.output)

    payload = json.loads(eval_path.read_text(encoding="utf-8"))
    summary = payload["summary"]

    entry = {
        "label": args.label,
        "generated_at": payload.get("generated_at", datetime.utcnow().isoformat() + "Z"),
        "total": summary["total"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "pass_rate": summary["pass_rate"],
    }

    history = load_history(history_path)
    history.append(entry)

    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("w", encoding="utf-8") as f:
        for row in history:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    latest = history[-1]
    previous = history[-2] if len(history) > 1 else None
    delta = None
    if previous:
        delta = round(latest["pass_rate"] - previous["pass_rate"], 2)

    lines = [
        "# Monthly Evaluation Scorecard",
        "",
        f"- Label: **{latest['label']}**",
        f"- Generated: `{latest['generated_at']}`",
        f"- Pass rate: **{latest['pass_rate']}%**",
        f"- Passed/Total: **{latest['passed']}/{latest['total']}**",
    ]

    if delta is not None:
        trend = "improved" if delta > 0 else "regressed" if delta < 0 else "unchanged"
        lines.append(f"- Trend vs previous: **{delta:+.2f}% ({trend})**")

    lines += [
        "",
        "## By Rule Type",
        "",
        "| Rule Type | Pass Rate | Passed | Total |",
        "|---|---:|---:|---:|",
    ]

    for rule, stats in summary["by_rule"].items():
        lines.append(f"| {rule} | {stats['pass_rate']}% | {stats['passed']} | {stats['total']} |")

    lines += [
        "",
        "## Trend History",
        "",
        "| Label | Pass Rate | Passed/Total |",
        "|---|---:|---:|",
    ]

    for row in history[-12:]:
        lines.append(f"| {row['label']} | {row['pass_rate']}% | {row['passed']}/{row['total']} |")

    lines += [
        "",
        "## Failure Causes",
        "",
        "| Cause | Count |",
        "|---|---:|",
    ]

    for cause, count in summary["causes"].items():
        lines.append(f"| {cause} | {count} |")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {history_path}")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
