# Parva Sheets

Spreadsheet-friendly examples for calling Project Parva from Google Sheets and
Excel. These scripts use public stable v3 API routes only.

These examples are not marketplace packages. They are copy-paste starting
points for internal spreadsheets, vendor audits, and public-beta evaluation.

## Functions

Google Apps Script exposes these custom functions:

```text
=BS_TO_AD("2082-01-01")
=AD_TO_BS("2025-04-14")
=IS_NEPALI_HOLIDAY("2082-01-01")
=NEPALI_FISCAL_YEAR("2082-04-01")
=WORKING_DAY_NP("2082-01-02")
```

Pass `TRUE` as the second argument to return metadata columns where the
spreadsheet format allows it:

```text
=BS_TO_AD("2082-01-01", TRUE)
```

The metadata row includes source tier, confidence, review-required status,
claim boundary, and a not-authority marker when the API returns those fields.

## Boundary

Parva Sheets is decision support for deterministic Nepali time behavior. It is
not government, legal, tax, banking, payroll, religious, or future-date
authority. Future-sensitive or unsupported cases should be reviewed before use
in operational systems.

## Configuration

Google Apps Script reads `PARVA_API_BASE_URL` from Script Properties. If absent,
it uses:

```text
https://api.prabinghimire1.com.np
```

Excel Office Script helpers accept the base URL as an optional argument.

