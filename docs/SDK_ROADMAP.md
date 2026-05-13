# SDK Roadmap

Project Parva is intended to support simple SDK adoption for teams replacing fragile calendar-table logic.

## Target SDKs

| SDK | Status |
| --- | --- |
| JavaScript and TypeScript | Priority public SDK target |
| Python | Priority public SDK target |
| PHP | Planned for common Nepali web stacks |
| Java | Planned for enterprise systems |
| .NET | Planned for later enterprise integrations |

## Modes

| Mode | Purpose |
| --- | --- |
| Local mode | Stable published calendar data and deterministic conversion logic |
| API mode | Live validation, source metadata, and public calendar surfaces |
| Private deployment mode | Controlled validation, reconciliation, and sensitive calendar-risk workflows |

## Public-Safe Examples

SDK examples should call only public-safe surfaces:

- calendar today
- AD to BS conversion
- BS to AD conversion
- fiscal-year logic where public
- RuleLang public rule capabilities and bounded public rule evaluation
- future-BS capabilities summary

SDK examples should not call private future-BS predictions, exports, model runs, backtests, client comparison workflows, corrected-value outputs, or schedule-impact simulations.

The goal is a drop-in replacement path for existing fragile calendar logic while preserving claim boundaries and source policy.
