# PTS-005 Trust Log

## Purpose

The trust log records public release events and hash chain metadata.

## Required fields

- `entry_hash`
- `release_id`
- `event_type`

## Validation

Hash chains must verify locally. Preview signatures must be labeled `unsigned_preview`.
