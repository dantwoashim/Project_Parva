# Future-BS Blinded Audit Tool

This tool compares an external BS month-length assumption sheet against the public-safe risk alpha and returns aggregate review metrics only.

It does not return corrected future month values by default. It does not publish a future calendar. Every result is labeled:

```text
computed_prediction_not_official
```

## Input

CSV columns:

```text
bs_year,bs_month,month_length
```

The committed sample file is synthetic and uses non-calendar demo years.

## Run

```bash
python tools/future_bs_audit/blinded_audit.py tools/future_bs_audit/sample_external_sheet.synthetic.csv
```

## Output

The default output is aggregate-only:

- total months checked
- agreement count
- disagreement count
- disagreement distribution by year
- boundary-sensitive count
- year-total anomaly count
- high-risk month count
- corrected values included, always false by default

Agreement means the submitted assumption is compatible with the public risk alpha. It does not mean Parva returned or revealed a corrected future value.

## Safety Boundary

Use real external files locally when authorized by the data owner. Do not commit real client data, private future values, corrected future values, or full private audit outputs.
