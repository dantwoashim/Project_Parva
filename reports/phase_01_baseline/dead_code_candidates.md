# Phase 01 Dead-Code Candidate Inventory



No files are deleted in Phase 01. These are review targets only.



| Path | Evidence | Risk of deletion | Recommended action | Phase |
| --- | --- | --- | --- | --- |
| backend/app/future_bs/legacy_cycle_predictor.py | no or only self filename references found in grep sample; path indicates compatibility or legacy surface | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| backend/app/future_bs/risk_thresholds.py | no or only self filename references found in grep sample | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| backend/tools/build_archive_harvest_queue.py | no or only self filename references found in grep sample; path indicates archive/historical material | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| backend/tools/discover_koirala_holiday_archives.py | no or only self filename references found in grep sample; path indicates archive/historical material | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| data/future_bs/benchmarks/accuracy_thresholds.json | no or only self filename references found in grep sample | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| data/future_bs/benchmarks/official_holdout_v1.csv | no or only self filename references found in grep sample | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| data/future_bs/public/official_holdout_2078_2083.csv | no or only self filename references found in grep sample | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| data/source_archive/README.md | no or only self filename references found in grep sample; path indicates archive/historical material | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| docs/COMPATIBILITY_BADGES.md | no or only self filename references found in grep sample; path indicates compatibility or legacy surface | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| docs/PROTOCOL_COMPATIBILITY.md | no or only self filename references found in grep sample; path indicates compatibility or legacy surface | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| frontend/scripts/golden_journeys.mjs | no or only self filename references found in grep sample | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| governance/COMPATIBILITY_CERTIFICATION.md | no or only self filename references found in grep sample; path indicates compatibility or legacy surface | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| registry/compatibility/README.md | no or only self filename references found in grep sample; path indicates compatibility or legacy surface | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| scripts/future_bs/parse_archive_panchanga.py | no or only self filename references found in grep sample; path indicates archive/historical material | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| scripts/future_bs/tune_risk_thresholds.py | no or only self filename references found in grep sample | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| scripts/release/package_source_archive.py | no or only self filename references found in grep sample; path indicates archive/historical material | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| scripts/release/verify_source_archive.py | no or only self filename references found in grep sample; path indicates archive/historical material | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| scripts/run_golden_journeys.py | no or only self filename references found in grep sample | low | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| tests/accuracy/test_future_bs_official_holdout.py | no or only self filename references found in grep sample | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| tests/fixtures/bs_historical.json | no or only self filename references found in grep sample; path indicates archive/historical material | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| tests/unit/future_bs/test_risk_thresholds.py | no or only self filename references found in grep sample | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |
| tests/unit/scripts/test_package_source_archive.py | no or only self filename references found in grep sample; path indicates archive/historical material | medium | review in Phase 03/04 before deletion | Phase 03 or Phase 04 |

## Supplemental Tool Attempts

These commands were attempted after the generated candidate list to satisfy the optional dead-code discovery guidance in the Phase 01 prompt. No deletion was performed.

| Command | Status | Evidence | Classification |
| --- | --- | --- | --- |
| `py -3.11 -m vulture backend scripts tests` | blocked | `No module named vulture` | environment issue |
| `npx --prefix frontend depcheck` | fail | `Path . does not contain a package.json file` after npx resolved `depcheck@1.4.7` | environment/tool invocation issue |
| `rg "TODO\|FIXME\|DEPRECATED\|compatibility\|legacy\|archive\|historical" . --glob ...` | pass | Returned 891 matches across docs, SDK compatibility paths, source archive notes, future-BS research, and compatibility wrappers. The output is too broad for deletion decisions and should feed Phase 03/04 triage. | repo inventory signal |
