#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="benchmark/output"
mkdir -p "$OUT_DIR"

echo "[1/4] Running evaluation_v4 (2025-2027)"
PYTHONPATH=backend python3 backend/tools/evaluate_v4.py --year-from 2025 --year-to 2027 --output-dir "$OUT_DIR"

echo "[2/4] Triaging mismatches"
python3 backend/tools/triage_mismatches.py

echo "[3/4] Generating scorecard entry"
python3 scripts/generate_scorecard.py --label "benchmark-run"

echo "[4/4] Checking accuracy gate"
python3 scripts/check_accuracy_gate.py

echo "Benchmark run completed. Outputs:"
ls -1 "$OUT_DIR"
