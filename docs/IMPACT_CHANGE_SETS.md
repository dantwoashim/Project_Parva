---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Impact Change Sets

A change set describes one or more temporal changes.

Required change fields:

- `change_type`
- `entity_type`
- `entity_id`

Supported change families include source changes, fact changes, rule changes, profile changes, confidence changes, conflict changes, and release diffs.

The public API enforces bounded simulations and does not inspect private dependencies.
