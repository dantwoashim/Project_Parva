# Docs Link Fix

## Current State

The observed docs failures for `frontend/dist` and `data/ephemeris/jpl/` did
not reproduce under the current tree:

- `frontend/dist` exists after the frontend build flow.
- `data/ephemeris/jpl/` exists in this workspace.
- `python scripts/check_docs_links.py` passed.

## Policy

No generated build directory was blindly created for the checker. The public
verification gate builds frontend assets through the documented frontend build
flow, and docs link verification is clean.

Public verification does not require private source archives or private
Future-BS artifacts.

## Evidence

- `python scripts/check_docs_links.py`: pass.
- `python scripts/release/verify_public.py`: pass, including frontend build.

