# Architecture Migration Status

This file records the current state of the repository reorganization so future
changes do not repeat unsafe mechanical moves.

## Completed

- Removed repo-local Python auto-reexec behavior from `sitecustomize.py`.
- Consolidated security policy ownership into root `SECURITY.md`.
- Moved tracked MoHA 2080-2083 public holiday PDFs into
  `data/source_archive/moha/` with checksum metadata.
- Added `artifacts/POLICY.md`.
- Added `docs/architecture/ARCHITECTURE.md`.
- Moved the Future BS implementation to `app.research.future_bs`.
- Kept `app.future_bs` as a compatibility namespace for existing imports.
- Merged the former backend-local test folder into `tests/backend_runtime`.
- Renamed the local-kernel test folder to `tests/local_kernel`.

## Held Deliberately

- Stable domain modules such as `calendar`, `rules`, `festivals`,
  `canonicalization`, `boundary`, `explainability`, and `timegraph` were not
  moved because current services and proof code import them directly.
- `constraints`, `forge`, `bitplanes`, and related proof-demo modules were not
  moved because workflow and verification scripts still depend on their
  historical `app.*` paths.
- SDK, MCP, CLI, and benchmark paths were not physically moved in this pass
  where existing package metadata, docs, or registry submission paths depend on
  their current locations.

## Next Safe Steps

1. Inventory scripts into CI-referenced, docs-referenced, and orphan groups.
2. Move one tooling family at a time into `tools_lib` while keeping thin
   command wrappers in `scripts/`.
3. Add import-direction checks for new lane directories.
4. Move stable domain packages only after services import the new canonical
   path directly and compatibility shims are covered by tests.
