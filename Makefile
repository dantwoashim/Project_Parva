PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif command -v python3.11 >/dev/null 2>&1; then echo python3.11; else echo python; fi)
NPM ?= $(shell $(PYTHON) scripts/resolve_npm_command.py)

.PHONY: install install-backend install-sdk install-frontend dev dev-backend dev-frontend dev-local \
	test test-backend test-frontend lint lint-backend lint-frontend build build-frontend \
	verify verify-public verify-backend verify-frontend verify-sdk verify-docs verify-full \
	preflight-production smoke build-cloudrun-image clean

install: install-backend install-sdk install-frontend

install-backend:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[test,dev]

install-sdk:
	$(PYTHON) -m pip install -e sdk/python
	$(PYTHON) -m pip install -e packages/parva-python
	$(NPM) --prefix packages/parva-js ci

install-frontend:
	$(NPM) --prefix frontend ci

dev: dev-backend

dev-backend:
	uvicorn app.main:app --app-dir backend --reload --port 8000

dev-frontend:
	$(NPM) --prefix frontend run dev

dev-local:
	scripts/run-local-launch.sh

test: test-backend test-frontend

test-backend:
	$(PYTHON) -m pytest -q

test-frontend:
	$(NPM) --prefix frontend test -- --run

lint: lint-backend lint-frontend

lint-backend:
	$(PYTHON) -m ruff check backend tests scripts sdk

lint-frontend:
	$(NPM) --prefix frontend run lint

build: build-frontend

build-frontend:
	$(NPM) --prefix frontend run build

verify:
	$(PYTHON) scripts/verify_environment.py
	$(PYTHON) scripts/release/check_repo_hygiene.py
	$(PYTHON) scripts/security/scan_repo_secrets.py
	$(PYTHON) scripts/check_path_leaks.py
	$(PYTHON) scripts/release/check_cloudrun_blueprint.py
	$(PYTHON) scripts/release/check_documented_routes.py
	$(PYTHON) scripts/release/check_backend_smoke.py
	$(PYTHON) scripts/release/check_sdk_install.py
	$(PYTHON) -m ruff check backend tests scripts sdk
	$(PYTHON) -m pytest -q
	$(NPM) --prefix frontend run lint
	$(NPM) --prefix frontend test -- --run
	$(NPM) --prefix frontend run build

verify-public:
	$(PYTHON) scripts/release/verify_public.py

verify-backend:
	$(PYTHON) scripts/verify_environment.py
	$(PYTHON) scripts/release/check_repo_hygiene.py
	$(PYTHON) scripts/check_docs_links.py
	$(PYTHON) scripts/release/check_render_blueprint.py
	$(PYTHON) scripts/release/check_documented_routes.py
	$(PYTHON) scripts/release/check_backend_smoke.py
	$(PYTHON) -m ruff check backend tests scripts sdk packages/parva-python
	$(PYTHON) -m pytest -q

verify-frontend:
	$(NPM) --prefix frontend run lint
	$(NPM) --prefix frontend test -- --run
	$(NPM) --prefix frontend run build

verify-sdk:
	$(PYTHON) scripts/release/check_sdk_install.py
	$(PYTHON) -m pytest packages/parva-python/tests -q
	$(NPM) --prefix packages/parva-js test

verify-docs:
	$(PYTHON) scripts/check_docs_links.py
	$(PYTHON) scripts/check_path_leaks.py

verify-full: verify

preflight-production:
	PARVA_ENV=production \
	PARVA_SOURCE_URL=https://example.com/source \
	PARVA_ROUTE_PROFILE=public_reference \
	PARVA_RATE_LIMIT_BACKEND=redis \
	PARVA_REDIS_URL=redis://localhost:6379/0 \
	PARVA_REQUIRE_PRECOMPUTED=false \
	PARVA_PROVENANCE_ATTESTATION_KEY=test-provenance-key \
	CORS_ALLOW_ORIGINS=https://example.com \
	PARVA_PLACE_SEARCH_ALLOW_REMOTE=false \
	PARVA_PLACE_SEARCH_PROVIDER_CHAIN=offline \
	PARVA_PLACE_SEARCH_PROVIDER_POLICY=offline_only \
	$(PYTHON) scripts/release/check_production_preflight.py

smoke:
	$(PYTHON) scripts/live_smoke.py --base http://127.0.0.1:8000

build-cloudrun-image:
	docker build -f Dockerfile.cloudrun -t project-parva-cloudrun .

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov build dist output reports tmp
	rm -rf backend/project_parva.egg-info sdk/python/build
