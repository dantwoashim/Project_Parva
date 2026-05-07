# External Sheet Audit

Parva can compare external BS month-length sheets against its computed prediction artifacts.

Supported row shape:

```text
bs_year, baishakh, jestha, ashadh, shrawan, bhadra, ashwin, kartik, mangsir, poush, magh, falgun, chaitra
```

Disagreement classes include:

- `AGREE_GREEN`
- `AGREE_YELLOW`
- `PARVA_HIGH_CONFIDENCE_DISAGREES`
- `BOTH_UNCERTAIN`
- `THEIR_VALUE_PLAUSIBLE`
- `METHOD_REGIME_RISK`

The audit is for review prioritization and financial model risk. It must not be used to label external future data as official.
