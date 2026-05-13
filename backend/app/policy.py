"""Policy metadata helpers for informational usage responses."""

from __future__ import annotations

DEFAULT_POLICY = {
    "usage": "informational",
    "advisory": "For religious observance, consult local authorities/panchang.",
    "publication_status": "computed_prediction_not_official",
    "claim_boundary": (
        "Project Parva is not an official government calendar publication. "
        "Official publications and institutional policy override computed outputs."
    ),
    "official_authority": False,
    "version": "2028.1",
    "disclaimer_url": "/v3/api/policy",
    "route_policy_url": "/v3/api/policy",
}


def get_policy_metadata() -> dict:
    """Return standardized policy metadata payload."""
    return dict(DEFAULT_POLICY)


def get_route_access_manifest() -> dict:
    """Return a concise public route access manifest for clients."""
    return {
        "access_model": "public_compute_with_admin_mutations",
        "families": [
            {"family": "calendar", "read_access": "public", "write_access": "none"},
            {"family": "enterprise", "read_access": "public", "write_access": "public"},
            {
                "family": "future_bs",
                "read_access": "public_summary_only",
                "write_access": "private_disabled_by_default",
            },
            {"family": "billing", "read_access": "public", "write_access": "public"},
            {"family": "personal", "read_access": "public", "write_access": "public"},
            {"family": "provenance", "read_access": "public", "write_access": "admin"},
            {"family": "admin", "read_access": "admin", "write_access": "admin"},
        ],
    }
