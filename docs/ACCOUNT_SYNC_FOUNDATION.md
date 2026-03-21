# Account Sync Foundation

Parva now exposes a concrete member-state persistence contract for two modes:

- `guest_local`: browser device cache only
- `account_remote`: account-backed persistence with async hydrate/save semantics

## Store Contract

A member store can implement:

- `load()`: synchronous bootstrap state for initial render
- `hydrate(currentState)`: optional async refresh for account-backed state
- `save(state, context)`: persist the normalized member state
- `describe()`: expose store metadata for diagnostics and release review

## Account-Backed Shape

The normalized account payload now reserves:

- `mode`
- `accountId`
- `syncEnabled`
- `profileVersion`
- `encryptionProfile`
- `lastSyncedAt`

## Release Expectation

Week 9 is complete when premium-facing flows no longer assume browser local storage is the only persistence target. The current repo satisfies that by shipping a real `account_remote` store contract while keeping guest device cache as the default runtime mode.
