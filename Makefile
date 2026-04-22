PYTHON ?= python3.11
NPM ?= npm

.PHONY: install install-backend install-sdk install-frontend dev dev-backend dev-frontend \
	test test-backend test-frontend lint lint-backend lint-frontend build build-frontend \
	verify preflight-production smoke build-cloudrun-image clean

install: install-backend install-sdk install-frontend

install-backend:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[test,dev]

install-sdk:
	$(PYTHON) -m pip install -e sdk/python

install-frontend:
	$(NPM) --prefix frontend ci

dev: dev-backend

dev-backend:
	uvicorn app.main:app --app-dir backend --reload --port 8000

dev-frontend:
	$(NPM) --prefix frontend run dev

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

preflight-production:
	PARVA_ENV=production \
	PARVA_SOURCE_URL=https://example.com/source \
	PARVA_RATE_LIMIT_BACKEND=redis \
	PARVA_REDIS_URL=redis://localhost:6379/0 \
	PARVA_REQUIRE_PRECOMPUTED=false \
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
