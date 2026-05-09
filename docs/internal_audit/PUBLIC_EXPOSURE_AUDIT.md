# Public Exposure Audit

Date: 2026-05-09

Scope: README, docs, public examples, API routing, OpenAPI behavior, tracked future-BS artifacts, tracked source archives, fixtures, and public capability payloads.

This audit is public-safe. It records exposure categories and actions without listing sensitive future values.

## Summary

| Category | Risk level | Finding | Action taken |
| --- | --- | --- | --- |
| README positioning | Medium | Previous public copy was safe but still framed future-BS details more prominently than needed. | Rewritten around Nepali temporal infrastructure, calendar risk, public/private boundary, and narrow research result. |
| Public API route boundary | High | Private future-BS routes exist in code and must never be public by default. | Verified default settings keep experimental routes disabled and private schemas hidden. Added focused public-safety tests. |
| Public capability payloads | Medium | Capability endpoints must describe methodology only, not private route inventory or future values. | Verified and updated payloads to metadata-only shape with `computed_prediction_not_official`. |
| OpenAPI schema | High | Public OpenAPI must not list prediction, export, backtest, model-run, residual, compare, or schedule-impact routes. | Verified public OpenAPI hides private routes by default. Added tests for default and explicit private-schema behavior. |
| Raw source archives | Medium | Tracked PDFs and HTML source captures add weight and expose acquisition material that is not needed for public demo. | Removed tracked source archives from Git tracking and ignored `data/source_archive/`. Local files can remain for internal runs. |
| Source inventory files | Medium | Tracked acquisition target inventories expose collection strategy. | Removed tracked source inventory files from Git tracking and ignored `data/source_inventory/`. |
| Witness extraction outputs | Medium | Tracked witness CSV/JSONL files expose extraction outputs that are better kept as internal artifacts. | Removed tracked witness outputs from Git tracking. Existing `.gitignore` covers witness artifact patterns. |
| Public docs | Medium | Required docs needed clearer claim, source, risk-label, reconciliation, and SDK boundaries. | Added or updated public-safe docs without exact private thresholds or future vectors. |
| Public examples | Low | Examples should demonstrate public shape only. | Added safe examples for conversion, fiscal capabilities, source policy, and future-BS capabilities. |
| Test fixtures | Low | Existing BS future fixtures are public-shape samples in published windows, not future vectors. | Kept fixtures and added tests to prevent public examples from adding future vectors. |
| Generated junk | Low | Local cache and zip artifacts were present in the working tree. | Removed local cache directories, `.pyc` files, and root archive junk. |
| Client-specific naming | High | Public repo must not mention specific prospects or client strategy. | Added tests for README and ran repository grep for client-specific terms. |

## Files Removed From Git Tracking

- `data/future_bs/witnesses/*`
- `data/source_archive/*`
- `data/source_inventory/*`

These files are ignored for public repo safety. Internal acquisition and validation runs can still use local copies or private storage.

## Route Boundary Result

Public by default:

- `/v3/api/calendar/*`
- `/v3/api/enterprise/*`
- `/v3/api/festivals/*`
- `/v4/api/future-bs/capabilities`
- `/v5/api/calendar-model-risk/capabilities` in the full public profile

Private by default:

- direct future month-length prediction
- full future range prediction
- CSV/XLSX future exports
- model runs
- backtests and residuals
- detailed explain and boundary-risk outputs
- loan or schedule-impact simulation
- external sheet import or comparison workflows
- corrected-value outputs
- private model internals

## Remaining Public Risk

The repository still contains future-BS engine source code because Project Parva is open-source. Public safety is handled through route gating, artifact hygiene, claim-boundary docs, ignored private artifacts, and tests. If the strategy changes to a closed-source model, the private engine modules and optimization scripts should move to a private repository.
