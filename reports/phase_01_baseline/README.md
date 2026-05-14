# Phase 01 Baseline Truth Freeze



Generated at: `2026-05-14T00:56:19+00:00`



This directory freezes the current repository truth before broad refactor or hardening phases. It is an audit baseline, not a product-behavior change.



## Repository fingerprint



| Field | Value |
| --- | --- |
| git_branch | main |
| git_commit | 101069faed51285e3895f46bcf107f92b833a579 |
| git_status_short | (clean) |
| python_version | Python 3.10.10 |
| python_executable | C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe |
| node_version | v25.2.1 |
| npm_version | 11.10.0 |
| phase_python_command | py -3.11 |
| phase_python_version | Python 3.11.4 |
| phase_python_executable | C:\Users\prabi\AppData\Local\Programs\Python\Python311\python.exe |
| platform | Windows-10-10.0.26200-SP0 |
| route_profile_default | developer_preview |
| render_route_profile | developer_preview |



## Lockfiles present



- `frontend/package-lock.json`
- `packages/parva-js/package-lock.json`
- `requirements/constraints.txt`



## CI workflows present



- `.github/workflows/ci.yml`
- `.github/workflows/trust-drift.yml`
- `.github/workflows/verify-public.yml`



## Package metadata



```json

{
  "backend": {
    "dependencies": [
      "fastapi>=0.135.1",
      "uvicorn>=0.23.0",
      "pydantic>=2.0.0",
      "pyswisseph>=2.10.0",
      "redis==7.4.0",
      "psycopg[binary]==3.3.4",
      "timezonefinder==8.2.0",
      "tzdata>=2024.1"
    ],
    "name": "project-parva",
    "optional_dependencies": {
      "data": [
        "pyarrow>=16.0.0"
      ],
      "dev": [
        "mypy>=1.11.0",
        "pip-audit>=2.8.0",
        "ruff>=0.8.0",
        "setuptools>=82.0.1"
      ],
      "ops": [
        "aiohttp>=3.13.5"
      ],
      "research": [
        "numpy>=1.26.0"
      ],
      "test": [
        "httpx>=0.27.0",
        "pytest>=9.0.3"
      ]
    },
    "requires_python": ">=3.11,<3.12",
    "version": "3.0.0"
  },
  "frontend": {
    "dependencies": {
      "date-fns": "^4.1.0",
      "leaflet": "^1.9.4",
      "prop-types": "^15.8.1",
      "react": "^19.2.0",
      "react-dom": "^19.2.0",
      "react-leaflet": "^5.0.0",
      "react-router-dom": "^7.9.5"
    },
    "devDependencies": {
      "@eslint/js": "^9.39.1",
      "@testing-library/jest-dom": "^6.9.1",
      "@testing-library/react": "^16.3.0",
      "@testing-library/user-event": "^14.6.1",
      "@types/react": "^19.2.5",
      "@types/react-dom": "^19.2.3",
      "@vitejs/plugin-react": "^5.1.1",
      "eslint": "^9.39.1",
      "eslint-plugin-react-hooks": "^7.0.1",
      "eslint-plugin-react-refresh": "^0.4.24",
      "globals": "^16.5.0",
      "jsdom": "^27.0.1",
      "playwright": "^1.58.2",
      "vite": "^7.2.4",
      "vitest": "^3.2.4"
    },
    "name": "frontend",
    "scripts": {
      "build": "vite build",
      "dev": "vite",
      "lint": "eslint .",
      "preview": "vite preview",
      "test": "vitest run",
      "test:a11y:live": "node scripts/accessibility_walkthrough.mjs",
      "test:visual": "vitest run src/test/visual/VisualRegression.test.jsx",
      "test:watch": "vitest"
    },
    "version": "3.0.0"
  },
  "parva-js": {
    "dependencies": {},
    "devDependencies": {
      "typescript": "^5.9.3"
    },
    "name": "@project-parva/parva-js",
    "scripts": {
      "build": "tsc -p tsconfig.json",
      "test": "npm run build && node --test tests/client.test.mjs"
    },
    "version": "0.1.0-alpha.0"
  },
  "parva-python": {
    "dependencies": [],
    "name": "project-parva-python-sdk",
    "version": "0.1.0a0"
  }
}

```



## Report files



- `canonical_runtime_discovery.md`
- `data_and_source_artifact_inventory.json`
- `data_and_source_artifact_inventory.md`
- `dead_code_candidates.json`
- `dead_code_candidates.md`
- `dead_code_tool_attempts.json`
- `duplicate_truth_paths.json`
- `duplicate_truth_paths.md`
- `fingerprint_command_attempts.json`
- `frontend_surface_inventory.json`
- `frontend_surface_inventory.md`
- `generated_artifacts_policy_gaps.json`
- `generated_artifacts_policy_gaps.md`
- `next_phase_red_check_targets.md`
- `public_private_research_boundary.json`
- `public_private_research_boundary.md`
- `risk_register_initial.md`
- `route_profile_inventory.json`
- `route_profile_inventory.md`
- `scorecard_initial.md`
- `sdk_inventory.json`
- `sdk_inventory.md`
- `security_surface_inventory.md`
- `subsystem_inventory.md`
- `subsystem_maturity_draft.yaml`
- `test_lane_inventory.json`
- `test_lane_inventory.md`
- `verification_matrix.json`
- `verification_matrix.md`
