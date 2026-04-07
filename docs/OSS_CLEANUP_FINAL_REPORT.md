# OSS Cleanup Final Report

This report summarizes the public-repo cleanup and OSS hardening pass completed on `repo-cleanup/oss-hardening`.

## Summary Of Cleanup Work

- tightened repo hygiene with a broader `.gitignore`, a top-level `Makefile`, and a safe `.env.example`
- added repo health automation for backend smoke checks, secret scanning, route/documentation parity, source archive validation, SDK install validation, and generated-artifact hygiene
- updated CI to run practical checks that match the public contributor workflow
- rewrote public-facing docs so the repository now states stable, beta, experimental, and legacy surfaces more honestly
- added open-source boundary documents, self-hosting guidance, support policy, release process notes, limitations, commercial boundary notes, and dataset/license guidance
- added issue templates, a PR checklist, and `CODEOWNERS` for contributor readiness
- normalized Python imports and cleaned up unused symbols so the backend and test tree pass `ruff`
- stabilized full-suite validation by fixing two stale integration assumptions and extending a few slow frontend test timeouts

## What Was Deleted

Tracked source deletions in this cleanup branch were intentionally minimal.

Local generated or junk artifacts removed from the worktree:

- `.pytest_cache/`
- `backend/project_parva.egg-info/`
- `benchmark/__pycache__/`
- `scripts/__pycache__/`
- `sdk/__pycache__/`
- `tests/__pycache__/`
- `dist/`
- `output/`
- `reports/`
- `tmp/`

## What Was Added

- `.env.example`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/bug-report.md`
- `.github/ISSUE_TEMPLATE/documentation-issue.md`
- `.github/ISSUE_TEMPLATE/feature-request.md`
- `.github/ISSUE_TEMPLATE/festival-date-discrepancy.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `Makefile`
- `docs/COMMERCIAL_OFFERING.md`
- `docs/DATA_SOURCES_AND_LICENSES.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/OPEN_SOURCE_SCOPE.md`
- `docs/OSS_CLEANUP_FINAL_REPORT.md`
- `docs/PRIVATE_MIGRATION_CANDIDATES.md`
- `docs/RELEASE_PROCESS.md`
- `docs/REPO_INVENTORY_AND_VISIBILITY_AUDIT.md`
- `docs/ROUTE_ACCESS.md`
- `docs/SECRET_AND_SENSITIVE_AUDIT.md`
- `docs/SELF_HOSTING.md`
- `docs/STABILITY.md`
- `docs/STALE_AND_DEPRECATED_ITEMS.md`
- `docs/SUPPORT_POLICY.md`
- `scripts/release/check_backend_smoke.py`
- `scripts/security/scan_repo_secrets.py`

## What Remains Risky

- `data/source_archive/secondary/` still contains raw third-party HTML snapshots with copied markup and embedded page-level tokens
- `data/source_archive/ratopati/event_days_2000_2100.json` may still need redistribution review before heavier promotion
- the public docs are materially better aligned now, but any future route exposure change can drift again unless the current contract checks remain enforced
- the reference frontend is reproducible and validated, but it is still a beta reference app rather than a polished end-user product

## What Should Move To A Private Or Internal Repo Later

- `data/source_archive/secondary/`
- any future operational runbooks, support playbooks, billing workflows, or hosted-service-only analytics material
- any future admin-only consoles or moderation overlays not required for the AGPL open-source core

See `docs/PRIVATE_MIGRATION_CANDIDATES.md` for the maintained list.

## Follow-Up Work Before Heavy Public Promotion

- scrub or migrate `data/source_archive/secondary/` out of the public repo
- complete a redistribution review for provider-derived archive data, especially the Ratopati archive
- keep the hosted deployment and README in sync whenever public routes, access policy, or supported versions change
- add release tagging and changelog discipline around stable `/v3/api/*` changes so downstream integrators can track compatibility more easily
- expand self-hosting notes with optional production deployment examples once the preferred hosting path is stable

## Validation Snapshot

The repository was validated with:

- `python scripts/verify_environment.py`
- `python scripts/release/check_repo_hygiene.py`
- `python scripts/security/scan_repo_secrets.py`
- `python scripts/check_path_leaks.py`
- `python scripts/release/check_documented_routes.py`
- `python scripts/release/check_backend_smoke.py`
- `python scripts/release/check_sdk_install.py`
- `python -m ruff check backend tests scripts sdk`
- `pytest -q`
- `npm --prefix frontend run lint`
- `npm --prefix frontend test -- --run`
- `npm --prefix frontend run build`
