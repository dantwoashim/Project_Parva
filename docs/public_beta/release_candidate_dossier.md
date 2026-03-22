# Release Candidate Technical Dossier

Generated at: `2026-03-21T11:07:05.999834+00:00`

## Candidate Identity

- Candidate date: 2026-03-21
- Candidate SHA: 479038c4f9a9ea44ddbba9ed07b727caebed01a3
- Candidate tag: unassigned
- Prepared from clean checkout: no

## Runtime Matrix

- Python: 3.11.4
- Node: 20.20.1
- Operating system: Windows-10-10.0.26200-SP0
- Browser smoke environment: playwright-chromium

## Provenance

- Manifest version: 2026-03-20
- Canonical engine id: parva-v3-canonical
- Dataset hash: 53d7bd5ab9e386a3fb80233bfe739ee3b5041f19460e960e76815023aef6158e
- Rules hash: f55fabcb335f106d934bed214c5541c1d275eff2a0b6ba9f9db5e6a87c3dffa9
- Dependency lock hash: 4ca433f7f02478aac7a36d6932eb5faea0c3db1eba225d5dc5611b9407585e48
- Attestation mode: hmac-sha256
- Attestation key id: redacted for public dossier
- Verification timestamp: 2026-03-21T11:05:17.591699+00:00

## Release Gates

- `scripts/verify_environment.py`: passed
- `scripts/release/check_repo_hygiene.py`: passed
- `scripts/release/check_render_blueprint.py`: passed
- `scripts/release/check_sdk_install.py`: passed
- `scripts/release/check_contract_freeze.py`: passed
- `scripts/release/check_provenance_readiness.py`: passed
- backend tests: passed (6/6 contract checks)
- frontend clean install: passed
- frontend lint/tests/build: passed
- frontend bundle budget: passed
- security audit: passed
- browser smoke: passed
- golden journeys: passed
- launch signoff: passed
- source archive: present

## User-Facing Risk Review

- degraded-state behavior reviewed: yes
- no hidden fallback date behavior confirmed: yes
- accessibility/dialog regression check: yes
- launch-critical journeys reviewed: yes
- timezone rendering spot-check: yes
- known limits accepted for this candidate: See docs/public_beta/month9_release_dossier.md.

## Artifact Inventory

- Source archive: `dist/project-parva-3.0.0-source.zip`
- Public-beta dossier: `docs/public_beta/month9_release_dossier.md`
- Conformance report: `reports/conformance_report.json`
- Authority dashboard: `docs/public_beta/authority_dashboard.md`
- Dashboard metrics: `docs/public_beta/dashboard_metrics.md`
- Browser smoke output: `reports/release/browser_smoke.json`
- Golden journeys output: `reports/release/golden_journeys.json`
- Bundle budget report: `reports/release/frontend_bundle_budget.json`
- Security audit report: `reports/security_audit.json`
- Launch signoff document: `docs/LAUNCH_SIGNOFF.md`

## Decision

- Release candidate approved: no
- Approver: pending_human_review
- Notes: Candidate artifact generated from a partial or local verification run.
