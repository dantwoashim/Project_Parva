# Phase 01 Handoff: Phase 02 Red-Check Targets



## Failed or blocked baseline commands



| Command run | Requested command | Status | Category | Summary |
| --- | --- | --- | --- | --- |
| py -3.11 scripts/check_path_leaks.py | python scripts/check_path_leaks.py | fail | private-data issue | parva_codex_phase_files\phase_06_trust_data_governance_and_source_authority.md:151: rg "data/source_archive\|data/future_bs/private\|/Users/\|C:\\\|private" data docs schemas specs backend frontend packages scripts tests \|\| true |
| py -3.11 scripts/check_docs_links.py | python scripts/check_docs_links.py | fail | repo issue | docs\strategy\PROJECT_PARVA_10_10_SOTA_MASTER_PLAN.md:817: missing path docs/internal_archive |
| py -3.11 scripts/release/verify_public.py | python scripts/release/verify_public.py | fail | private-data issue | [verify-public] FAIL: path leak scan exited 1 |



## Static red-check targets



| Target | Phase | Reason |
| --- | --- | --- |
| Public verification gate | Phase 02 | Make `scripts/release/verify_public.py` green from a clean public clone. |
| Route profile contract | Phase 02 | Convert route inventory into failing tests/snapshots. |
| Docs links | Phase 02 | Fix any link check failures found in this baseline. |
| Private/research markers | Phase 02 | Ensure private, wide, and research tests are excluded from public CI. |
| OpenAPI drift | Phase 02 | Pin public OpenAPI output for safe profiles. |
