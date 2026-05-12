# Parva Conformance Suite

The Parva conformance suite is a public-safe set of cases for checking calendar behavior outside the hosted API.

It gives SDK authors, private deployments, and reviewers a small baseline they can run locally. The suite is intentionally conservative: it uses published-range dates and synthetic shape-only cases where future-BS risk is involved.

## Run

```bash
python tools/conformance_runner/run.py
```

Optional API mode:

```bash
PARVA_CONFORMANCE_BASE_URL=http://localhost:8000 python tools/conformance_runner/run.py --api
```

Default mode uses local backend functions. API mode is optional and currently checks public conversion endpoints where practical.

## Coverage

| Area | Files |
| --- | --- |
| BS to AD conversion | `conversion/bs_to_ad_cases.json` |
| AD to BS conversion | `conversion/ad_to_bs_cases.json` |
| Round trips | `conversion/round_trip_cases.json` |
| Invalid BS dates | `validation/invalid_bs_dates.json` |
| Fiscal boundaries | `fiscal/fiscal_boundary_cases.json` |
| Release manifest shape | `release/release_manifest_cases.json` |
| Future-BS risk shape | `future-risk-shape/public_safe_cases.json` |
| Panchanga response shape | `panchanga-shape/public_safe_shape_cases.json` |

## Public Safety Boundary

- Cases use historical, published-range, or synthetic inputs.
- Future-BS risk cases validate public shape only.
- Future-BS risk cases do not include raw future month values, corrected values, or full future vectors.
- Future-BS risk cases require `publication_status = computed_prediction_not_official`.
- The suite is not an official government calendar publication.
- Official publication overrides computed output.

## SDK Use

SDKs should treat this suite as a baseline compatibility pack:

1. Load the JSON cases.
2. Run local SDK operations against the case inputs.
3. Compare outputs or response shape according to each case.
4. Preserve source policy and publication status in any public result.

Future versions may add a stricter conformance manifest, more published-range cases, and language-specific harnesses.
