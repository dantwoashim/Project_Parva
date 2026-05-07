# Calendar VaR

Calendar VaR estimates financial exposure from future BS month-length uncertainty.

Practical score:

```text
probability_of_mismatch
* one_day_interest_exposure
* number_of_affected_contracts
* operational_irreversibility_score
* official_publication_delay_risk
```

Risky months should use a no-break policy:

- store `calendar_run_id`,
- keep `publication_status`,
- keep prediction sets,
- mark reconciliation required,
- keep dual schedules where impact is material,
- recalculate after official publication.
