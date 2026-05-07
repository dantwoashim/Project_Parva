# Future BS Accuracy and Readiness

The accuracy target is month-first, not year-first.

Tracked metrics:

- `overall_top1_accuracy`
- `green_zone_accuracy`
- `green_zone_coverage`
- `boundary_case_accuracy`
- `year_exact_accuracy`
- `false_green_rate`
- `mismatched_months`

Current claim posture:

- Strict official holdout is useful but too small for a broad public 99% claim.
- The official/printed final-test corpus must reach at least 528 month cases before a final 99%+ market claim is allowed.
- Broad all-reference backtests are stress tests, not official claim evidence.

Invalid future year totals are never claimable. If a predicted year totals outside 365/366 days, the year is marked `RED`, `claimable=false`, and `manual_review_required=true`.
