# Loan Impact Simulation

The loan-impact simulator estimates how calendar mismatches can affect installment schedules and interest calculations.

## Supported Methods

- `actual_365`
- `actual_360`
- `actual_actual`
- `30_360`
- `monthly_flat`
- `product_specific`

## Input

```json
{
  "loan_start_bs": "2085-05-01",
  "term_months": 240,
  "principal": 1000000,
  "annual_rate": 12,
  "day_count_method": "actual_365",
  "external_years": [
    {
      "bs_year": 2085,
      "months": [31, 32, 31, 32, 31, 31, 30, 30, 29, 30, 30, 30]
    }
  ]
}
```

## Output

The response summarizes:

- mismatches affecting the schedule
- first impacted installment
- maximum due-date shift
- estimated interest difference
- risk level
- period-level mismatch detail

This is a screening tool. It does not replace product-specific amortization rules, legal contract review, or regulatory validation.
