# PTS-009 RuleLang

## Purpose

RuleLang is a safe structured rule format for institutional temporal decisions.

## Required fields

- `rule_id`
- `version`
- `status`
- `inputs`
- `outputs`
- `steps`
- `risk_policy`
- `claim_boundary`

## Safety

Rules must not execute arbitrary code, shell commands, filesystem access, network calls, or environment access. Loops must be bounded.
