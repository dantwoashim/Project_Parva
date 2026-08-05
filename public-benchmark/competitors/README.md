# Named-Tool BS Conformance Run

This harness executes four published npm packages against the same BS
`2078-2083` month fixture used by Project Parva.

Pinned implementations:

- `nepali-date-converter@3.4.0`
- `@sonill/nepali-dates@1.0.7`
- `nepali-date-library@1.1.15`
- `@remotemerge/nepali-date-converter@1.2.1`

The runner uses each package's published BS-to-AD conversion API. It converts
the first day of a month and the first day of the next month, then derives the
month length from the Gregorian-day difference. The Python comparison runner
scores those results against
`data/future_bs/public/official_holdout_2078_2083.csv` and runs Parva's
chronological future-BS replay as a separate track.

Historical conformance and forecasting answer different questions. Published
lookup packages already contain the target years, so they are omitted from the
forecast score rather than assigned a failure.

The scored set accepts only version-pinned public developer interfaces that can
be replayed in CI. Consumer calendar websites, including Hamro Patro and Nepali
Patro, are excluded because this review found no qualifying public interface for
either site. The harness never treats scraped web pages as reproducible evidence.

Run:

```bash
cd public-benchmark/competitors
npm ci --ignore-scripts
cd ../..
py -3.11 public-benchmark/runners/run_competitor_comparison.py
```

Outputs:

- `public-benchmark/results/competitor-comparison.json`
- `public-benchmark/results/competitor-comparison.md`
- `frontend/src/data/competitorBenchmark.json`

The JSON output includes package versions, all mismatches, year-by-year replay
splits, and SHA-256 hashes for the fixture, lockfile, and runners.
