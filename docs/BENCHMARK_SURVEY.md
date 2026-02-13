# Benchmark Survey (Year 3 Week 1)

## Surveyed Reference Styles
- Panchanga/almanac verification against official published calendars (Rashtriya Panchang)
- Public holiday verification against government notices (MoHA)
- Cross-system comparative checks (patro apps, community calendars)
- Formulaic calendar checks (Hebrew/Islamic deterministic conversions)

## Observations
- Many systems publish dates but do not expose reproducible harnesses.
- Source disagreements often come from interpretation rules, not arithmetic failure.
- A useful benchmark must track both exact match and classified disagreement reasons.

## Implication for Parva
Parva benchmark needs:
- Source-linked test cases
- Machine-runnable packs
- Published taxonomy for disagreements
- Reproducible harness with deterministic outputs

This survey informed `docs/BENCHMARK_SPEC.md` and the pack/harness structure in `/benchmark`.
