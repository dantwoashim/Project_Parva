#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[Month9] 1/8 Rule ingestion drift + computed target gate"
PYTHONPATH=backend python3 scripts/rules/ingest_rule_sources.py --check --target 300 --computed-target 300

echo "[Month9] 2/8 Backend test suite"
PYTHONPATH=backend python3 -m pytest -q

echo "[Month9] 3/8 Conformance pack"
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py

echo "[Month9] 4/8 Contract freeze"
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py

echo "[Month9] 5/8 Accuracy benchmark"
PYTHONPATH=backend python3 scripts/generate_accuracy_report.py

echo "[Month9] 6/8 Authority dashboard"
PYTHONPATH=backend python3 scripts/generate_authority_dashboard.py

echo "[Month9] 7/8 Evaluator dossier"
PYTHONPATH=backend python3 scripts/release/generate_month9_dossier.py

echo "[Month9] 8/8 Frontend tests + build"
npm --prefix frontend test -- --run
npm --prefix frontend run build

echo "[Month9] All release gates passed."
