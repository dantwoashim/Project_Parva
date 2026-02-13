#!/usr/bin/env python3
"""Fail if pass-rate regresses beyond allowed threshold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Accuracy regression gate")
    parser.add_argument("--history", default="reports/evaluation_history.jsonl")
    parser.add_argument("--max-regression", type=float, default=0.0, help="Allowed pass-rate drop in percentage points")
    args = parser.parse_args()

    history = load_history(Path(args.history))
    if len(history) < 2:
        print("Not enough history to compare; gate passes.")
        return 0

    prev = history[-2]
    curr = history[-1]
    delta = curr["pass_rate"] - prev["pass_rate"]

    print(f"Previous: {prev['pass_rate']}% | Current: {curr['pass_rate']}% | Delta: {delta:+.2f}%")

    if delta < -abs(args.max_regression):
        print("Accuracy regression gate failed.")
        return 1

    print("Accuracy regression gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
