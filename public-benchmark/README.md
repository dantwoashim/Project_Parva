# Nepali Time Reliability Benchmark v0

This benchmark makes Nepali time reliability visible as a public software
category. It tests deterministic calendar behavior, source awareness,
uncertainty handling, review gates, and machine-readable structure.

Categories:

- BS/AD conversion
- valid and invalid BS dates
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

Run the static baseline:

```bash
python public-benchmark/runners/run_against_static_baseline.py
```

Run against a local or deployed Parva base URL:

```bash
python public-benchmark/runners/run_against_parva.py --base-url https://api.prabinghimire1.com.np
```

The Parva runner maps every task in `benchmark.json` to a concrete public
endpoint and emits per-task signals for correctness, source awareness,
uncertainty handling, review gates, and machine-readable structure. Use
`--fail-under <percent>` in CI when a minimum score should fail the command.
