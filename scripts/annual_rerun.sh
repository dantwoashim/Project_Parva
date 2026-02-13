#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/7] OCR ingest"
PYTHONPATH=backend python3 backend/tools/ingest_moha_pdfs.py || true

echo "[2/7] Source normalization"
PYTHONPATH=backend python3 backend/tools/normalize_sources.py

echo "[3/7] OCR quality metrics"
PYTHONPATH=backend python3 backend/tools/ocr_quality_check.py

echo "[4/7] Evaluation v4"
PYTHONPATH=backend python3 backend/tools/evaluate_v4.py --year-from 2025 --year-to 2027

echo "[5/7] Discrepancy triage"
python3 backend/tools/triage_mismatches.py

echo "[6/7] Scorecard update"
python3 scripts/generate_scorecard.py --label "$(date '+%Y-%m') annual-rerun"

echo "[7/8] Accuracy gate"
python3 scripts/check_accuracy_gate.py

echo "[8/8] Provenance snapshot refresh"
PYTHONPATH=backend python3 backend/tools/generate_snapshot.py

echo "Annual rerun completed."
