# go-nepali Issue #15 Regression PR Assessment

## Summary

`opensource-nepal/go-nepali` issue
[#15](https://github.com/opensource-nepal/go-nepali/issues/15) reported an
AD-to-BS boundary conversion case:

- AD `2024-06-13` -> BS `2081-02-31`
- AD `2024-06-14` was reported as BS `2081-03-01`
- Reporter expected AD `2024-06-14` -> BS `2081-02-32`

The issue is closed and was fixed by upstream PR
[#16](https://github.com/opensource-nepal/go-nepali/pull/16).

## Current Upstream Status

- Repository: <https://github.com/opensource-nepal/go-nepali>
- Checked commit: `e85acd189810d0698b79276a4af242fee1c6b60a`
- Latest local result: `go test ./...` passed
- Current behavior appears fixed for AD `2024-06-14`

The existing upstream tests did not include the exact AD `2024-06-14` to BS
`2081-02-32` regression case.

## PR Decision

A tiny test-only PR was appropriate because:

- the current behavior passes,
- upstream tests run cleanly,
- the exact public issue case is deterministic,
- the change does not modify runtime behavior,
- the change does not add a dependency,
- the change does not make a calendar authority claim.

Opened PR:

- <https://github.com/opensource-nepal/go-nepali/pull/34>

## Validation

Run in the upstream checkout:

```bash
go test ./...
```

Result: passed.

## Boundary

This PR only adds historical regression coverage for a fixed public issue. It
does not imply upstream endorsement of Project Parva, does not introduce a
Project Parva dependency, and does not make an authority claim.
