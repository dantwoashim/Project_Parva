# Release Process

Project Parva releases should be reproducible from a clean clone.

## Expected release flow

1. Start from a clean git working tree.
2. Install backend and SDK dependencies.
3. Install frontend dependencies with `npm ci`.
4. Run `make verify`.
5. Build any source archives with `scripts/release/package_source_archive.py`.
6. Verify the archive with `scripts/release/verify_source_archive.py`.
7. Publish the exact source URL used by the deployment through `PARVA_SOURCE_URL`.

## Required gates

- repo hygiene check
- secret scan
- path leak check
- route/doc parity
- backend smoke
- SDK wheel-install smoke
- Python lint and tests
- frontend lint, tests, and build

## Release artifacts

- source archive from `scripts/release/package_source_archive.py`
- optional submission bundle from `scripts/release/package_submission_bundle.py`
- generated reports under `reports/` if you need them for a release review

Generated artifacts are not source and should not be committed back into the repo.
