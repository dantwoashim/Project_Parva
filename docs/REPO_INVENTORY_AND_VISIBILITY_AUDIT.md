# Repo Inventory And Visibility Audit

This document classifies the current repository tree from a public open-source perspective.

## Classification legend

- `keep public`
- `keep public but clean up`
- `move to private/internal repo`
- `delete as junk/generated`
- `unclear / needs manual decision`

## Inventory

| Path | Purpose | Current status | Recommendation | Reason | Risk |
| --- | --- | --- | --- | --- | --- |
| `.github/` | Issue templates, PR template, and CI workflows | Public collaboration surface | keep public but clean up | Needed for contributor readiness and realistic automation | Medium |
| `.github/workflows/ci.yml` | CI entrypoint | Public repo control plane | keep public but clean up | Needed for trust and reproducibility; now includes hygiene, smoke, and secret scan gates | Medium |
| `.dockerignore` | Container build hygiene | Public build helper | keep public | Prevents local junk from inflating container context | Low |
| `.gitattributes` | Git content normalization | Public repo metadata | keep public | Helps keep line endings and archive behavior predictable | Low |
| `.gitignore` | Source hygiene | Public repo control plane | keep public | Prevents recommitting local junk and generated output | Low |
| `.nvmrc` | Node runtime hint | Public contributor helper | keep public but clean up | Useful for local setup as long as it stays aligned with the supported frontend runtime | Low |
| `.vibecop.yml` | Local tooling config | Public tooling metadata | unclear / needs manual decision | Safe to keep if the tool remains in use; otherwise it becomes noise | Low |
| `.env.example` | Safe config template | Public setup asset | keep public | Required for contributor and self-hosting clarity | Low |
| `Makefile` | Common repo tasks | Public setup asset | keep public | Makes install, lint, test, and verify flows discoverable | Low |
| `README.md` | Public project entrypoint | Public facing | keep public but clean up | Must stay truthful about stability, scope, and setup | High |
| `CONTRIBUTING.md` | Contributor workflow | Public facing | keep public but clean up | Needed for contributor readiness and evidence expectations | Medium |
| `SECURITY.md` | Security posture | Public facing | keep public but clean up | Needed for disclosure and support boundaries | Medium |
| `LICENSE` | Repository license | Public legal artifact | keep public | Required | Low |
| `THIRD_PARTY_NOTICES.md` | Third-party notice summary | Public legal artifact | keep public | Required for dependency/license clarity | Medium |
| `CHANGELOG.md` | Release/change history | Public project history | keep public but clean up | Useful, but should stay honest and current | Low |
| `Dockerfile` | Container build | Public deployment asset | keep public | Needed for reproducible builds and self-hosting | Medium |
| `render.yaml` | Example hosted deployment config | Public deployment asset | keep public but clean up | Safe as long as secrets remain operator-supplied | Medium |
| `pyproject.toml` | Python packaging and lint/test config | Public build asset | keep public | Core packaging metadata | Low |
| `requirements/` | Shared constraints | Public build asset | keep public | Reproducibility | Low |
| `backend/` | Backend package, tooling, and data-adjacent runtime support | Public OSS core | keep public | Central implementation of the public API and trust model | High |
| `backend/app/` | FastAPI runtime and domain logic | Public OSS core | keep public | Core product implementation | High |
| `backend/tests/` | Backend coverage | Public OSS core | keep public | Needed for trust and contribution | Low |
| `backend/tools/` | Backend maintenance and one-off tooling | Mixed public/internal quality | keep public but clean up | Valuable, but some tools are niche or historical | Medium |
| `frontend/` | Reference web client | Public OSS core | keep public | Important public surface and reproducible demo path | High |
| `frontend/src/` | Reference frontend source | Public OSS core | keep public | Core product surface | High |
| `frontend/public/` | Static public assets and portals | Public web assets | keep public but clean up | Valuable, but claims must stay aligned with runtime | Medium |
| `sdk/` | Public client SDK workspace | Public OSS core | keep public | Part of the published integration surface | High |
| `sdk/python/` | Python SDK | Public OSS core | keep public | Key developer surface | High |
| `scripts/` | Repo automation, release, and support utilities | Mixed public engineering surface | keep public but clean up | Useful, but should stay sharply separated from unsupported experiments | Medium |
| `scripts/release/` | Release and packaging automation | Public OSS core | keep public | Needed for reproducible public releases | High |
| `scripts/security/` | Security and audit helpers | Public OSS core | keep public | Needed for public repo trust | Medium |
| `scripts/telegram/bot_poc.py` | Telegram proof of concept | Public but unsupported | keep public but clean up | Not core, but acceptable as a labeled PoC | Low |
| `scripts/governance/` | Governance helpers | Public project process | keep public but clean up | Keep only if actively used | Medium |
| `docs/` | Public documentation | Public OSS core | keep public but clean up | Needs ongoing honesty and drift control | High |
| `docs/contracts/` | OpenAPI and route snapshots | Public contract artifacts | keep public | Useful for contract governance | Medium |
| `docs/KNOWN_LIMITS.md` | Backward-compatible docs pointer | Public compatibility artifact | keep public but clean up | Prevents old links from breaking while pointing readers to the new canonical limitations doc | Low |
| `data/` | Runtime datasets, inventories, and evidence artifacts | Public data surface | keep public but clean up | Core to trust and behavior, but some archived subtrees deserve stricter review | High |
| `data/festivals/` | Festival data and content | Public OSS core data | keep public | Required for runtime | High |
| `data/ground_truth/` | Validation/reference data | Public validation asset | keep public | Useful for testing and trust | Medium |
| `data/places/` | Place/gazetteer data | Public runtime data | keep public but clean up | Keep attribution and redistribution review in mind | Medium |
| `data/source_inventory/` | Provenance/source inventory metadata | Public trust artifact | keep public | Better public fit than raw scraped sources | Medium |
| `data/source_archive/moha/` | Official public holiday source PDFs | Public evidence asset | keep public but clean up | Public-facing provenance value, but redistribution basis should stay documented | Medium |
| `data/source_archive/ratopati/` | Provider-derived archive data | Public archive artifact | unclear / needs manual decision | Useful for provenance, but redistribution basis should be reviewed | High |
| `data/source_archive/secondary/` | Raw third-party HTML source snapshots | Public raw archive | move to private/internal repo | Includes copied third-party markup and embedded page-level tokens; not required by runtime | High |
| `data/transparency_log.json` | Public transparency artifact | Public trust artifact | keep public but clean up | Small and understandable, but should stay generated and documented | Medium |
| `benchmark/` | Benchmark harness and packs | Public engineering asset | keep public but clean up | Useful for performance work; generated results should stay out of git | Medium |
| `stitch/` | Design/reference artifacts and screenshots | Public reference asset | keep public but clean up | Useful context, but not normative product docs | Low |
| `tests/` | Integration, contract, and unit tests | Public OSS core | keep public | Required for contributor confidence | Low |
| `dist/` | Built archives or build output | Local generated artifact | delete as junk/generated | Should not be committed; already ignored and removed from the worktree | Medium |
| `output/` | Generated runtime output | Local generated artifact | delete as junk/generated | Not source | Medium |
| `reports/` | Generated reports | Local generated artifact | delete as junk/generated | Not source | Medium |
| `tmp/` | Temporary workspace output | Local generated artifact | delete as junk/generated | Not source | Low |
| `.pytest_cache/` | Test cache | Local generated artifact | delete as junk/generated | Not source | Low |
| `backend/project_parva.egg-info/` | Packaging residue | Local generated artifact | delete as junk/generated | Not source | Low |

## Overall recommendation

The repo should remain public and continue to publish the backend, frontend, SDK, tests, docs, and trust metadata. The main boundary to tighten further is raw third-party archival material under `data/source_archive/`, especially `secondary/`.
