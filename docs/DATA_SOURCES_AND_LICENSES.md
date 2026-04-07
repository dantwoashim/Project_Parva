# Data Sources And Licenses

Project Parva combines code, curated datasets, and source references. Contributors should treat those categories differently.

## Main categories

| Category | Examples | Notes |
| --- | --- | --- |
| First-party code and docs | `backend/`, `frontend/`, `sdk/`, most of `docs/` | Governed by the repository license |
| Official or public reference material | public holiday PDFs, source inventories, trust metadata | Verify redistribution rights before adding new raw source files |
| Provider-derived data | geocoding inputs, archived third-party source snapshots | Review redistribution and attribution carefully |
| Third-party software dependencies | `pyswisseph`, frontend npm packages | Follow upstream licenses and notices |

## Important current sources

- official/public holiday reference PDFs under `data/source_archive/moha/`
- curated source inventories under `data/source_inventory/`
- festival and variant data under `data/festivals/` and `data/variants/`
- Swiss Ephemeris through `pyswisseph` for astronomical calculations

## Contributor guidance

- Do not add proprietary datasets without explicit permission.
- Prefer inventories, checksums, and derived metadata over raw third-party page dumps.
- If you add a new source archive, document its license or redistribution basis.
- If you are unsure whether a source file belongs in the public repo, document it in [PRIVATE_MIGRATION_CANDIDATES.md](PRIVATE_MIGRATION_CANDIDATES.md).
