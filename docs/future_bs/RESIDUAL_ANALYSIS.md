# Future BS Residual Analysis

Residual analysis is the discipline that prevents Parva from pretending a weak
calendar prediction is stronger than it is.

The future-BS engine measures accuracy by month, not by year. Every mismatch is
stored with the BS year, month, official/reference month length, predicted month
length, predicted start date, official start date, ingress time, selected civil
rule, boundary distance, source quality, and the alternative rule that would
have matched.

Use:

```bash
python scripts/generate_residual_report.py \
  --train-start 2000 \
  --train-end 2077 \
  --test-start 2078 \
  --test-end 2083 \
  --source-policy official_only \
  --output data/future_bs/reports/official_residual_report.md
```

The generated report groups failures by BS month, ingress hour, boundary
distance, source type, and alternative civil rule. A 99%+ claim is only valid
when the official/printed benchmark has enough month cases and the report's
claim-readiness flag is true.
