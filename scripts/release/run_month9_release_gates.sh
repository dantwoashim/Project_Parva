#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[Month9] 1/12 Repo hygiene"
python3 scripts/release/check_repo_hygiene.py

echo "[Month9] 2/12 Render blueprint"
python3 scripts/release/check_render_blueprint.py

echo "[Month9] 3/12 SDK install surface"
python3 scripts/release/check_sdk_install.py

echo "[Month9] 4/12 License compliance"
PYTHONPATH=backend python3 scripts/release/check_license_compliance.py

echo "[Month9] 5/12 Backend test suite"
PYTHONPATH=backend python3 -m pytest -q

echo "[Month9] 6/12 Conformance pack"
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py

echo "[Month9] 7/12 Contract freeze"
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py

echo "[Month9] 8/12 Route inventory"
PYTHONPATH=backend python3 scripts/release/check_route_inventory.py

echo "[Month9] 9/12 Clean source archive"
python3 scripts/release/package_source_archive.py
python3 scripts/release/verify_source_archive.py

echo "[Month9] 10/12 Frontend lint"
npm --prefix frontend run lint

echo "[Month9] 11/12 Frontend tests"
npm --prefix frontend test -- --run

echo "[Month9] 12/12 Frontend build"
npm --prefix frontend run build

echo "[Month9] All release gates passed."
