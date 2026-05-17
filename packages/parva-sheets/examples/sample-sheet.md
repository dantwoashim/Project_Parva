# Sample Sheet

Paste the Google Apps Script in `google-apps-script/Code.gs`, then use:

| Cell | Formula | Expected shape |
| --- | --- | --- |
| A2 | `=BS_TO_AD("2082-01-01")` | AD date string |
| A3 | `=AD_TO_BS("2025-04-14")` | BS date string |
| A4 | `=IS_NEPALI_HOLIDAY("2082-01-01")` | Boolean |
| A5 | `=NEPALI_FISCAL_YEAR("2082-04-01")` | Fiscal-year label |
| A6 | `=WORKING_DAY_NP("2082-01-02")` | Boolean |
| A8 | `=BS_TO_AD("2082-01-01", TRUE)` | Answer plus metadata columns |

Metadata columns include `review_required`, `claim_boundary`, and
`not_authority`. Treat review-required rows as workflow prompts, not automatic
decisions.

