# Phase 16 Depth Hardening Plan

This pass closes the false-proof class first. The architecture must not make a weak or irrelevant source look stronger because it is wrapped in hashes.

## Completed In This Pass

- Dynamic source-docket coverage resolution for `convert_bs_to_ad`.
- Sample 2082 dockets are no longer promoted to `structured_official`.
- Out-of-coverage dates such as 2070 and 2099 degrade to `computed_uncertified` with review required.
- Backend membrane verification now replays the BS-to-AD computation and checks source docket resolution.
- Core BS-to-AD route exposes opt-in `proof=membrane`.
- Embed renderer no longer uses `innerHTML`.
- Source review queue has a committed public inventory.
- Semantic depth gate checks behavior-sensitive conditions instead of path presence only.

## Remaining Depth Work

- Extend replay verification beyond `convert_bs_to_ad`.
- Make the local browser kernel replay source coverage and conversion from shared static fixtures.
- Replace remaining solver demo paths with forge-generated bitplanes for holidays, Saturdays, working days, festival windows and review-required states.
- Expand TempC and notice ingestion from samples into reviewed structured extractors.
- Add SDK proof helpers for membrane verification and proof-pack loading.
- Build external witness intake only after local proof semantics are stable.

## Claim Boundary

Parva can now honestly claim one locally replay-verifiable proof-carrying conversion operation. It still cannot claim full external ceiling completion, official authority, legal/tax/payroll/banking authority, official future-date authority, external certification, real customers, or registry acceptance.
