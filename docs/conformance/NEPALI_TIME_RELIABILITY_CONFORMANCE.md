# Nepali Time Reliability Conformance

Project Parva conformance is a technical report format for checking whether a
system handles Nepali temporal workflows with clear source, confidence, range,
and review-boundary behavior.

It is not a certification program and does not create government, legal, tax,
banking, payroll, religious, or future-date authority.

## Levels

- [Bronze](BRONZE.md): conversion, invalid dates, supported range disclosure.
- [Silver](SILVER.md): holidays, fiscal years, working days, institution-profile awareness.
- [Gold](GOLD.md): source metadata, confidence metadata, review-required behavior, Future-BS boundaries.
- [Platinum](PLATINUM.md): panchanga, sunrise/location sensitivity, institution profiles, benchmark threshold, evidence-packet support.

Use:

```bash
python scripts/conformance/generate_conformance_report.py --input samples/conformance/vendor_input_sample.csv --json-out samples/conformance/conformance_report_sample.json --md-out samples/conformance/conformance_report_sample.md
```

