# Benchmark Summary

## Benchmark

`public-benchmark/benchmark.json` contains 64 public-safe tasks across:

- BS/AD conversion
- invalid BS dates
- holidays
- working days
- fiscal-year boundaries
- festival dates
- Panchanga/tithi at sunrise
- payroll and repayment review gates
- Future-BS unsupported/review-required behavior
- source/confidence/evidence metadata

## Scoring

- Correctness: 40
- Source awareness: 20
- Uncertainty handling: 20
- Review gate behavior: 10
- Machine-readable structure: 10

## Runner Results

- Static baseline: 19.38 percent.
- Parva runner: 87.19 percent, 64 tasks passed.

## Interpretation

The benchmark supports the argument that Nepali time should be called from deterministic infrastructure rather than guessed by general-purpose models. It does not prove official authority, full national coverage, or future civil calendar correctness.
