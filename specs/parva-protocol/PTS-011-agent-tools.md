# PTS-011 Agent Tools

## Purpose

Agent tools expose deterministic Parva services to humans and software agents without hallucinating temporal facts.

## Required tool fields

- `name`
- `description`
- `input_schema`
- `output_schema`
- `supported_mode`
- `claim_boundary`

## Safety

Agent tools must return decision status, reason codes, confidence, warnings, evidence references, and human-review flags.
