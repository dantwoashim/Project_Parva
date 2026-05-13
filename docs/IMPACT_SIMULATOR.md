# Temporal Impact Simulator

The Temporal Impact Simulator computes deterministic impact from registered public temporal dependencies.

It answers a narrow question: when a source, release, fact, rule, profile, confidence label, or conflict changes, which known Parva artifacts may need review?

It does not claim to know unregistered downstream systems.

## Inputs

- change sets
- semantic release diffs
- TimeGraph facts
- RuleLang traces
- evidence packet dependencies
- compliance profile dependencies

## Outputs

Impact runs include severity, reason codes, recommended actions, stale evidence status, and a claim boundary.

Stale evidence means the packet remains historically valid for the release that generated it, but should be regenerated before current operational use.

## Public boundary

Public mode uses public release artifacts, public TimeGraph, public RuleLang rules, and fixture-only simulations where needed.
