"""Policy metadata helpers for informational usage responses."""

from __future__ import annotations


DEFAULT_POLICY = {
    "usage": "informational",
    "advisory": "For religious observance, consult local authorities/panchang.",
    "version": "2028.1",
    "disclaimer_url": "/docs/POLICY.md",
}


def get_policy_metadata() -> dict:
    """Return standardized policy metadata payload."""
    return dict(DEFAULT_POLICY)
