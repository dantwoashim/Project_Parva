# Data Sources And Licenses

Project Parva combines code, curated datasets, and source references. Contributors should treat those categories differently.

## Main categories

| Category | Examples | Notes |
| --- | --- | --- |
| First-party code and docs | `backend/`, `frontend/`, `sdk/`, most of `docs/` | Governed by the repository license |
| Public fixtures | `tests/fixtures/`, small checked-in JSON or CSV test fixtures | Deterministic test inputs, not official authority |
| Public validation data | `data/validation/public/`, runtime-safe validation inputs | Public route quality and reliability inputs |
| Public generated data | Checked-in public artifacts and schemas | Only included when intentionally part of the public artifact |
| Official or public reference material | public holiday PDFs, source inventories, trust metadata | Verify redistribution rights before adding new raw source files |
| Private source archives | local `data/source_archive/` material | Optional for public development and gated by explicit env vars |
| Private research artifacts | local future-BS runs, model outputs, review queues | Not required for public verification and not public claim evidence |
| Provider-derived data | geocoding inputs, archived third-party source snapshots | Review redistribution and attribution carefully |
| Third-party software dependencies | `pyswisseph`, frontend npm packages | Follow upstream licenses and notices |

## Important current sources

- festival and variant data under `data/festivals/` and `data/variants/`
- runtime validation inputs under `data/validation/public/`
- test-only fixtures under `tests/fixtures/`
- public source policy and trace metadata under `backend/data/public_artifacts/`
- Swiss Ephemeris through `pyswisseph` for astronomical calculations

Private or optional source archives may exist locally under `data/source_archive/`, but they are not required for the public verification gate.

## Contributor guidance

- Do not add proprietary datasets without explicit permission.
- Prefer inventories, checksums, and derived metadata over raw third-party page dumps.
- If you add a new source archive, document its license or redistribution basis.
- If you are unsure whether a source file belongs in the public repo, open an issue with the source origin, redistribution basis, and whether a derived public-safe form is enough.
- Tests that depend on private source archives must be gated behind `PARVA_ENABLE_PRIVATE_SOURCE_TESTS=1` and should explain the expected `PARVA_SOURCE_ARCHIVE_DIR`.
