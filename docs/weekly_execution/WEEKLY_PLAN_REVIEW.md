# Weekly Plan Review (Year 1/2/3)

## Summary
- The plans are strong on cadence and quality gates.
- Year 1 is the right sequence: stabilize engine correctness before ecosystem expansion.
- Year 2/3 are ambitious but coherent for a moonshot track.

## What Is Strong
- Clear monthly and weekly structure with explicit deliverables.
- Definitions of Done are measurable.
- Good emphasis on validation, discrepancy logging, and benchmark publishing.
- Correct strategic order: `accuracy -> contracts -> trust -> scale`.

## Gaps to Fix Before Execution
1. `backend/app/festivals/repository.py` does **not** have `get_festival_dates()`; the method is `get_dates()`.
2. Year 1 Week 2 says remove all `festival_rules.json` references. Current `calculator_v2` still uses fallback to legacy rule coverage. Removing references now would drop coverage unless we migrate missing rules first.
3. Year 1 Week 2 says “redirect all calendar endpoints to V2”. For `/api/calendar/panchanga*`, this is ephemeris/panchanga logic, not festival V2 logic. Scope should be clarified to avoid unnecessary rewrites.
4. Plan assumes route contracts are unified in one pass. Current API uses mixed shapes (typed + dict). This should be split into:
   - `spec lock`
   - `compat wrappers`
   - `hard cutover` after contract tests.
5. Weekly plans mention multiple files/tools not guaranteed in active code path (legacy docs/tests). Distinguish:
   - runtime-critical
   - tests-only
   - docs-only

## Recommended Adjustments
1. Keep Week 1 exactly as audit/spec week (no hard code moves yet).
2. In Week 2, migrate runtime routes first; keep temporary compatibility wrappers.
3. Replace “remove legacy rules” with:
   - “migrate legacy rules into v3-compatible format”
   - “remove fallback only after parity test passes”.
4. Add a release blocker:
   - no route cutover without contract snapshot test green.
5. Track coverage explicitly:
   - festivals in `festival_rules_v3.json`
   - festivals only available via fallback.

## Decision
- Approved to execute Year 1 Week 1 now with the above corrections.
