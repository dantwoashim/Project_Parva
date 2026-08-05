# Nepali Time Reliability Benchmark v0

![Parva benchmark](results/benchmark.svg)

This benchmark makes Nepali time reliability visible as a public software
category. It tests deterministic calendar behavior, source awareness,
uncertainty handling, review gates, and machine-readable structure.

Categories:

- BS/AD conversion
- invalid BS dates and validation failure behavior
- public holidays
- working-day shifts
- fiscal-year boundaries
- repayment or payroll due-date logic
- festival dates
- panchanga or tithi queries
- Future-BS review-required behavior
- source, confidence, and review metadata

The benchmark does not require private data and does not claim legal, banking,
payroll, government, religious, or official future-date authority.

Current tracked comparison:

- Parva: 86.09%
- Static baseline: 19.38%
- Gap: 66.71 percentage points
- Tasks: 64
- Review gates: 10/10

Named-tool BS conformance and future-BS replay:

- Project Parva: 72/72 historical months
- `nepali-date-converter@3.4.0`: 72/72 historical months
- `@sonill/nepali-dates@1.0.7`: 56/72 historical months
- `nepali-date-library@1.1.15`: 72/72 historical months
- `@remotemerge/nepali-date-converter@1.2.1`: 72/72 historical months
- Project Parva chronological forecast replay: 72/72 with past-only training

The historical run measures current lookup/conversion output. The forecast run
is a separate evaluation because the four npm packages publish lookup tables
rather than forecast methods. Full results and mismatches are in
[results/competitor-comparison.md](results/competitor-comparison.md).

Run the static baseline:

```bash
python public-benchmark/runners/run_against_static_baseline.py
```

Run against the in-process public-reference Parva app:

```bash
python public-benchmark/runners/run_against_parva.py
```

Run against a deployed Parva base URL:

```bash
python public-benchmark/runners/run_against_parva.py --base-url https://api.prabinghimire1.com.np
```

Run the named-tool comparison:

```bash
cd public-benchmark/competitors
npm ci --ignore-scripts
cd ../..
py -3.11 public-benchmark/runners/run_competitor_comparison.py
```

The Parva runner maps every task in `benchmark.json` to a concrete public
endpoint and emits per-task signals for correctness, source awareness,
uncertainty handling, review gates, and machine-readable structure. Use
`--fail-under <percent>` in CI when a minimum score should fail the command.
