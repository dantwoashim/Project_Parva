# Future BS Risk Labels

Risk labels describe review posture. They are not official future publication.

Every future-BS output remains:

```text
computed_prediction_not_official
```

## GREEN

GREEN means the system sees low risk under its current public claim boundary. Internal checks agree, source uncertainty is low for the evaluated policy, and no immediate review trigger is present.

GREEN does not mean official. It does not override later official publication or institutional approval.

## YELLOW

YELLOW means review is recommended.

Typical reasons include:

- boundary-sensitive month-start behavior
- disagreement between computational and reference signals
- limited source support
- wider prediction set
- uncertain regime assignment
- operational impact if the month length differs by one day

## RED

RED means unsafe, non-claimable, or source-conflicted for the evaluated policy.

Typical reasons include:

- invalid year total
- source conflict
- out-of-distribution behavior
- high perturbation sensitivity
- weak evidence for a consequential month
- multiple subsystem disagreements

RED months should not be used as final future calendar authority. They require official publication, reviewed printed evidence, or an approved institutional policy.

Exact thresholds are private deployment configuration, not public documentation.
