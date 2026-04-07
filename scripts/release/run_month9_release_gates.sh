#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[Month9] 1/13 Repo hygiene"
python3 scripts/release/check_repo_hygiene.py

echo "[Month9] 2/13 Render blueprint"
python3 scripts/release/check_render_blueprint.py

echo "[Month9] 3/13 SDK install surface"
python3 scripts/release/check_sdk_install.py

echo "[Month9] 4/13 License compliance"
PYTHONPATH=backend python3 scripts/release/check_license_compliance.py

echo "[Month9] 5/13 Backend test suite"
PYTHONPATH=backend python3 -m pytest -q

echo "[Month9] 6/13 Conformance pack"
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py

echo "[Month9] 7/13 Contract freeze"
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py

echo "[Month9] 8/13 Route inventory"
PYTHONPATH=backend python3 scripts/release/check_route_inventory.py

echo "[Month9] 9/13 Documented routes"
PYTHONPATH=backend python3 scripts/release/check_documented_routes.py

echo "[Month9] 10/13 Clean source archive"
python3 scripts/release/package_source_archive.py
python3 scripts/release/verify_source_archive.py

echo "[Month9] 11/13 Frontend lint"
npm --prefix frontend run lint

echo "[Month9] 12/13 Frontend tests"
npm --prefix frontend test -- --run

echo "[Month9] 13/13 Frontend build"
npm --prefix frontend run build

echo "[Month9] All release gates passed."
