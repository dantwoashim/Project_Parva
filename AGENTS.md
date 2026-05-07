# AGENTS.md - Project Parva Operating Instructions

These instructions apply to this repository unless a more specific nested
`AGENTS.md` overrides them.

## Highest Priority

Always complete tasks in one shot when the user asks for one-shot or 100%
completion. A single response may run for hours if needed. Do not leave
required implementation, testing, artifact generation, or verification for a
later response unless the objective is impossible and the blocker is documented.

## Core Rule

Complete the actual objective, not a superficial version of it. Do not stop at
scaffolding, placeholder files, fake reports, optimistic documentation, or
untested code.

A task is complete only when:

1. The code works.
2. Relevant tests pass or failures are honestly documented.
3. Generated artifacts actually exist and are non-empty.
4. Commands in the documentation actually run.
5. Reports match the files and metrics in the repository.
6. Remaining blockers are exact and actionable.

## Truthfulness

Never claim:

- Tests pass unless they were run.
- A report was generated unless the file exists.
- An endpoint works unless it was exercised or tested.
- Accuracy was achieved unless metrics prove it.
- A file exists unless it was verified.

If a command fails, times out, or is not run, say so explicitly.

## Preservation

Preserve existing Project Parva functionality:

- BS/AD conversion
- AD/BS conversion
- fiscal-year logic
- known/published month-length lookup
- holidays
- public calendar surfaces
- panchanga/tithi/muhurta/kundali/festival routes if present
- enterprise routes
- frontend/demo surfaces
- SDK/client code
- deployment files
- documentation
- existing tests

Prefer additive changes. Do not remove or rename public behavior unless the
task explicitly requires it and compatibility is handled.

## Execution Loop

For implementation work, follow this loop:

1. Inspect the current repo.
2. Identify the true current state.
3. Implement the smallest useful change.
4. Run the relevant command or test.
5. Read failures carefully.
6. Fix the failure.
7. Rerun.
8. Verify artifacts and reports.
9. Document the final state truthfully.

## Runtime Discipline

Default API routes and demo-safe commands must not hang. Expensive computation
must be behind explicit script commands, flags, or environment variables.

If a route depends on a generated report, load the artifact by default. If the
artifact is missing, return a clear error explaining which command generates it.

## Accuracy Work

For prediction, validation, ranking, or accuracy work:

- Prevent leakage between training and hidden/evaluation data.
- Separate official, printed, institutional, third-party, needs-review, and
  experimental sources.
- Report overall accuracy, high-confidence accuracy, coverage, false-confidence
  rate, wrong high-confidence count, residuals, blockers, and data limitations.
- Prefer uncertainty over confident wrong output.
- Never fake a 99%+ claim.

Future BS predictions must remain labeled:

```text
publication_status = computed_prediction_not_official
```

## Artifact Rules

When a task produces JSON, Markdown, CSV, XLSX, PDF, or other artifacts:

1. Generate the files.
2. Verify they exist.
3. Verify they are non-empty.
4. Verify basic schema or format where practical.
5. Update reports only after verification.

Do not list missing files as generated.

## Final Report

Every major task should end with a concise report covering:

- What changed.
- What commands were run.
- What passed.
- What failed or was not run.
- What artifacts were generated.
- What remains incomplete.
- Exact next steps for any blocker.
