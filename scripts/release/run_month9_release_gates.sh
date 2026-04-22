#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[Month9] 1/15 Repo hygiene"
python3 scripts/release/check_repo_hygiene.py

echo "[Month9] 2/15 Render blueprint"
python3 scripts/release/check_render_blueprint.py

echo "[Month9] 3/15 Cloud Run blueprint"
python3 scripts/release/check_cloudrun_blueprint.py

echo "[Month9] 4/15 Production preflight"
PARVA_ENV=production \
PARVA_SOURCE_URL=https://example.com/source \
PARVA_RATE_LIMIT_BACKEND=redis \
PARVA_REDIS_URL=redis://localhost:6379/0 \
PARVA_REQUIRE_PRECOMPUTED=false \
PARVA_PLACE_SEARCH_ALLOW_REMOTE=false \
PARVA_PLACE_SEARCH_PROVIDER_CHAIN=offline \
PARVA_PLACE_SEARCH_PROVIDER_POLICY=offline_only \
python3 scripts/release/check_production_preflight.py

echo "[Month9] 5/15 SDK install surface"
python3 scripts/release/check_sdk_install.py

echo "[Month9] 6/15 License compliance"
PYTHONPATH=backend python3 scripts/release/check_license_compliance.py

echo "[Month9] 7/15 Backend test suite"
PYTHONPATH=backend python3 -m pytest -q

echo "[Month9] 8/15 Conformance pack"
PYTHONPATH=backend python3 scripts/spec/run_conformance_tests.py

echo "[Month9] 9/15 Contract freeze"
PYTHONPATH=backend python3 scripts/release/check_contract_freeze.py

echo "[Month9] 10/15 Route inventory"
PYTHONPATH=backend python3 scripts/release/check_route_inventory.py

echo "[Month9] 11/15 Documented routes"
PYTHONPATH=backend python3 scripts/release/check_documented_routes.py

echo "[Month9] 12/15 Clean source archive"
python3 scripts/release/package_source_archive.py
python3 scripts/release/verify_source_archive.py

echo "[Month9] 13/15 Frontend lint"
npm --prefix frontend run lint

echo "[Month9] 14/15 Frontend tests"
npm --prefix frontend test -- --run

echo "[Month9] 15/15 Frontend build"
npm --prefix frontend run build

echo "[Month9] All release gates passed."
