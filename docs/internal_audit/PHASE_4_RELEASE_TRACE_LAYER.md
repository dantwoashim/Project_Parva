# Phase 4 Release And Trace Layer Audit

## Phase Goal

Phase 4 adds the first public-safe release manifest, source registry, artifact hash verification tool, and calculation trace model layer.

The goal is machine-verifiable metadata. This phase does not publish private future-BS values, private model internals, source archive dumps, or client-specific material.

## Release Artifacts Created

- `data/public/releases/parva-bs-public-demo.manifest.json`
- `data/public/releases/parva-bs-public-demo.sources.json`

The public demo manifest includes:

- `release_id`
- `calendar`
- `coverage`
- `source_policy`
- `publication_status`
- `artifact_hashes`
- `generated_at`
- `schemas_used`
- `claim_boundary`

The manifest sets `future_values_included` to `false`.

## Source Registry Created

The source registry contains public-safe metadata for:

- Project Parva Temporal Specification v0.1
- Project Parva public conformance suite v0.1
- Project Parva public API contract

The registry does not include raw source archives, private source dumps, future vectors, corrected future values, or client-specific material.

## Schemas Created

- `schemas/release-manifest.schema.json`
- `schemas/source-registry.schema.json`
- `schemas/artifact-hash.schema.json`

`tools/validate_schemas.py` was updated to validate these schemas together with the existing public schema set.

`.gitattributes` was updated so public release JSON and schema JSON files keep stable LF line endings. This protects SHA-256 artifact verification from checkout-level line-ending conversion.

## Trace Model Status

Added:

- `backend/app/core/calculation_trace.py`
- `tests/unit/core/test_public_calculation_trace.py`

The model mirrors `schemas/calculation-trace.schema.json` and is additive. Existing API routes and existing runtime trace storage were not changed.

## Tools Created

- `tools/release/verify_release.py`
- `tools/release/README.md`

The verifier:

- loads release manifest JSON
- checks required manifest fields
- checks public claim boundary
- checks `future_values_included` is false
- loads every schema listed in `schemas_used`
- computes SHA-256 for every listed artifact
- compares computed hashes against manifest hashes
- validates listed source registry artifacts
- exits nonzero on missing files, malformed JSON, hash mismatch, or unsafe public content

Focused tests also verify that a hash mismatch fails.

## Documentation Created Or Updated

- `docs/RELEASE_MANIFESTS.md`
- `docs/SOURCE_REGISTRY.md`
- `docs/CALCULATION_TRACES.md`
- `docs/SDK_USAGE.md`
- `.gitattributes`

The docs explain release purpose, source registry purpose, artifact hashes, traces, official publication override, future-BS boundary, and alpha limitations.

## Commands Run

| Command | Result |
|---|---|
| `python tools/release/verify_release.py data/public/releases/parva-bs-public-demo.manifest.json` | Passed |
| `python tools/validate_schemas.py` | Passed, 12 schemas |
| `python tools/conformance_runner/run.py` | Passed, 27 of 27 cases |
| `PYTHONPATH=backend python -m pytest tests/unit/core/test_public_calculation_trace.py tests/unit/release/test_verify_release.py -q` | Passed, 3 tests |
| `PYTHONPATH=backend python -m pytest -q` | Passed, 660 passed and 7 skipped |
| `npm --prefix frontend run build` | Passed |

## Quality Review Performed

- Re-read the phase specification before implementation and before broad verification.
- Verified required release files exist and parse.
- Verified required schemas exist and validate.
- Verified the release verifier computes real SHA-256 values.
- Verified hash mismatch behavior with a focused unit test.
- Verified source registry entries are metadata-only and public-safe.
- Verified trace docs align with the schema shape and backend model.
- Removed or avoided raw future-year literals in the release verifier public-safety guard.
- Checked edited files for em dash characters.

## Repo-Wide Searches

The required searches were run for:

- stale deployment URL patterns
- prohibited client-name and overclaim patterns
- private or sensitive future-BS values in Phase 4 files
- em dash characters in edited Phase 4 docs and code

Classifications:

- Existing archived Cloud Run deployment notes and the legacy Cloud Build blueprint still contain stale deployment references. They were not introduced by Phase 4.
- Existing public-safety tests contain prohibited phrases as guardrail input strings. They were not introduced by Phase 4.
- Local phase prompt files contain instruction text and are untracked. They were not staged.
- Phase 4 files do not contain private future vectors, corrected future values, client-specific references, or broad future accuracy claims.

## Public Safety Status

Pass.

- No private future-BS values were added.
- No full future month-length table was added.
- No corrected future value was added.
- No private model internals were added.
- No client-specific data was added.
- Future-BS boundary remains `computed_prediction_not_official`.
- Official publication override is present in the manifest, source registry, and docs.

## Known Gaps

- The public release manifest is unsigned. It uses local SHA-256 verification only.
- The trace model is additive and schema-aligned, but route-level trace enrichment was not attached in this phase to avoid destabilizing public APIs.
- The source registry is metadata-only. It intentionally does not include raw external source archives.
- The manifest describes public demo and conformance metadata. It is not a complete official calendar data release.

## Next Recommended Phase

- Add optional public endpoints for release manifest retrieval if route exposure is reviewed.
- Add signed manifest support.
- Add SDK helpers to expose `release_id` and trace metadata consistently.
- Add language-specific conformance adapters that verify release metadata as part of SDK CI.
