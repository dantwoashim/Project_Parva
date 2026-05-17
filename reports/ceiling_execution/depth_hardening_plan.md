# Phase 16 Depth Hardening Plan

This pass closes the false-proof class first. The architecture must not make a weak or irrelevant source look stronger because it is wrapped in hashes.

## Completed In This Pass

- Dynamic source-docket coverage resolution for `convert_bs_to_ad`.
- Dynamic source-docket coverage resolution and replay capsules for `ad_to_bs`, `validate_bs_date`, `holiday`, `working_day`, `fiscal_year`, and `bs_months`.
- Sample 2082 dockets are no longer promoted to `structured_official`.
- Out-of-coverage dates such as 2070 and 2099 degrade to `computed_uncertified` with review required.
- Backend membrane verification now replays civil temporal computations and checks source docket resolution.
- Core conversion, validation, compliance holiday/working-day, fiscal-year, and BS-month routes expose opt-in proof modes.
- Embed renderer no longer uses `innerHTML`.
- Source review queue has a committed public inventory.
- Semantic depth gate checks behavior-sensitive conditions instead of path presence only.
- Working-day solver consumes generated causal bitplanes instead of fixed weekend offsets.
- TempC parses a minimal payroll-safe date grammar into a constraint query.
- Notice ingestion extracts structured source fields into review-required obligation artifacts.
- Python and JavaScript SDKs expose proof modes for the civil core.

## Remaining Depth Work

- Make the local browser kernel replay source coverage and full civil conversion from shared static fixtures, not only hash/proof-pack linkage.
- Expand causal bitplanes beyond the payroll-safe date workflow into festivals, fiscal periods, overlays, and source-backed/freshness planes.
- Expand TempC beyond the payroll-safe date grammar.
- Add full SDK-side replay helpers for proof packs and Timepacks.
- Build external witness intake only after local proof semantics are stable.

## Claim Boundary

Parva can now honestly claim replay-verifiable civil temporal proof mode for the stable core operations implemented in this pass. It still cannot claim full external ceiling completion, official authority, legal/tax/payroll/banking authority, official future-date authority, external certification, real customers, package publication, or registry acceptance.
