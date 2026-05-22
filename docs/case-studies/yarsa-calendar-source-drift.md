# Yarsa nepal-compliance Calendar Source Drift Case

## Summary

Project Parva's benchmark work led to a merged standalone calendar consistency
benchmark in Yarsa Labs' `nepal-compliance` repository.

Links:

- Issue: <https://github.com/yarsa/nepal-compliance/issues/257>
- PR: <https://github.com/yarsa/nepal-compliance/pull/258>
- Merge commit: `c220a9e`

## What Was Found

The benchmark compared duplicated Nepali calendar month tables:

- Backend source: CSV calendar data.
- Frontend source: JS calendar table.

Inside the overlapping supported range, the two sources differed for:

- BS year: `2087`
- BS month: `Mangsir`
- Backend CSV: `29` days
- Frontend JS table: `30` days

The script also showed later conversion examples shifting by one day:

- BS `2088-01-01`: backend AD `2031-04-15`, frontend AD `2031-04-16`
- BS `2089-12-30`: backend AD `2033-04-13`, frontend AD `2033-04-14`

## What Was Contributed

The upstream PR added:

- a standalone script,
- no runtime behavior change,
- no added dependency,
- informational reporting for range differences,
- failure reporting for overlapping month-length mismatches,
- shifted conversion examples where the table divergence changes later dates.

## What This Means For Project Parva

This validates a core conformance idea: Nepali date systems need checks for
source drift, duplicated calendar data, and conversion boundary effects.

The case is now represented in Parva as:

- a public source-drift fixture,
- a benchmark documentation example,
- an executable consistency check in the public issue conformance runner.

## What This Does Not Mean

- Yarsa did not change its product to depend on Project Parva.
- This case does not claim production impact.
- This case does not make Parva an official date authority.
- This case is not a claim that all Yarsa date logic is wrong.

## Links

- Issue #257: <https://github.com/yarsa/nepal-compliance/issues/257>
- PR #258: <https://github.com/yarsa/nepal-compliance/pull/258>
- Merge commit: `c220a9e`
