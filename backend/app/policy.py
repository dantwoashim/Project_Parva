"""Policy metadata helpers for informational usage responses."""

from __future__ import annotations

DEFAULT_POLICY = {
    "usage": "informational",
    "advisory": "For religious observance, consult local authorities/panchang.",
    "version": "2028.1",
    "disclaimer_url": "/v3/api/policy",
    "route_policy_url": "/v3/api/policy",
    "access_model": "public_compute_with_admin_mutations",
}


def get_policy_metadata() -> dict:
    """Return standardized policy metadata payload."""
    return dict(DEFAULT_POLICY)


def _describe_requirement(requirement) -> str:
    if not requirement.required:
        return "public"
    if requirement.admin_only:
        return "admin"
    if requirement.scope:
        return f"scoped:{requirement.scope}"
    return "authenticated"


def _manifest_probe_paths(compat_prefix: str) -> tuple[str, str]:
    if compat_prefix == "/api/provenance":
        return ("/v3/api/provenance/root", "/v3/api/provenance/transparency/append")
    canonical_prefix = f"/v3{compat_prefix}"
    return (canonical_prefix, canonical_prefix)


def get_route_access_manifest() -> dict[str, object]:
    """Return a truthful route-access summary generated from runtime policy code."""
    from app.bootstrap.access_control import classify_request
    from app.bootstrap.router_registry import iter_route_policy_specs

    families: list[dict[str, str]] = []
    for spec in iter_route_policy_specs():
        compat_prefix = spec["path"]
        if compat_prefix.startswith("/v3/"):
            continue

        canonical_prefix = f"/v3{compat_prefix}"
        read_probe, write_probe = _manifest_probe_paths(compat_prefix)
        read_requirement = classify_request(read_probe, "GET")
        write_requirement = classify_request(write_probe, "POST")
        families.append(
            {
                "family": spec["registration_name"],
                "policy_name": spec["policy_name"],
                "compat_prefix": compat_prefix,
                "canonical_prefix": canonical_prefix,
                "read_probe_path": read_probe,
                "write_probe_path": write_probe,
                "read_access": _describe_requirement(read_requirement),
                "write_access": _describe_requirement(write_requirement),
            }
        )

    return {
        "profile": "v3",
        "compat_alias": "/api",
        "access_model": "public_compute_with_admin_mutations",
        "generated_from": "app.bootstrap.router_registry.iter_route_policy_specs",
        "experimental_tracks": {
            "enabled_by_default": False,
            "prefixes": ["/v2", "/v4", "/v5"],
            "access": "preview_only",
        },
        "notes": [
            "The supported v3 read and compute surface is public by default and should be treated as rate-limited public infrastructure.",
            "Mutating provenance routes remain admin-only even though provenance reads are public.",
            "Experimental version tracks are disabled by default and are not part of the supported public contract.",
        ],
        "families": families,
    }
