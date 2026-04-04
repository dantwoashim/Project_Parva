"""Route classification and authentication helpers."""

from __future__ import annotations

import hmac
from dataclasses import dataclass

from fastapi import Request

from .settings import AppSettings

PUBLIC_HEALTH_PATHS = {
    "/",
    "/health",
    "/health/live",
    "/health/ready",
    "/health/startup",
    "/docs",
    "/openapi.json",
    "/v3/docs",
    "/v3/openapi.json",
}
EXPERIMENTAL_PREFIXES = ("/v2/", "/v4/", "/v5/")
PROVENANCE_READ_PREFIXES = (
    "/api/provenance/root",
    "/v3/api/provenance/root",
    "/api/provenance/proof",
    "/v3/api/provenance/proof",
    "/api/provenance/verify/",
    "/v3/api/provenance/verify/",
    "/api/provenance/batch-verify",
    "/v3/api/provenance/batch-verify",
    "/api/provenance/transparency/log",
    "/v3/api/provenance/transparency/log",
    "/api/provenance/transparency/audit",
    "/v3/api/provenance/transparency/audit",
    "/api/provenance/transparency/replay",
    "/v3/api/provenance/transparency/replay",
    "/api/provenance/transparency/anchors",
    "/v3/api/provenance/transparency/anchors",
    "/api/provenance/dashboard",
    "/v3/api/provenance/dashboard",
)
PROVENANCE_PREFIXES = ("/api/provenance", "/v3/api/provenance")


@dataclass(frozen=True)
class Principal:
    principal_type: str
    principal_id: str
    scopes: frozenset[str]

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes


@dataclass(frozen=True)
class AccessRequirement:
    required: bool
    policy_name: str
    scope: str | None = None
    admin_only: bool = False


@dataclass(frozen=True)
class RoutePolicy:
    name: str
    path: str
    requirement: AccessRequirement
    match: str = "prefix"
    methods: frozenset[str] = frozenset({"*"})

    def matches(self, path: str, method: str) -> bool:
        normalized_method = method.upper()
        if "*" not in self.methods and normalized_method not in self.methods:
            return False
        if self.match == "exact":
            return path == self.path
        return path.startswith(self.path)


def route_policy(
    *,
    name: str,
    path: str,
    requirement: AccessRequirement,
    match: str = "prefix",
    methods: tuple[str, ...] = ("*",),
) -> RoutePolicy:
    return RoutePolicy(
        name=name,
        path=path,
        requirement=requirement,
        match=match,
        methods=frozenset(method.upper() for method in methods),
    )


def _is_public_path(path: str) -> bool:
    if path in PUBLIC_HEALTH_PATHS:
        return True
    if path.startswith(("/assets/", "/favicon", "/manifest", "/sw.js")):
        return True
    return False


ROUTE_POLICY_REGISTRY: tuple[RoutePolicy, ...] = (
    route_policy(
        name="reliability_read",
        path="/api/reliability",
        requirement=AccessRequirement(required=False, policy_name="reliability_read"),
    ),
    route_policy(
        name="reliability_read_v3",
        path="/v3/api/reliability",
        requirement=AccessRequirement(required=False, policy_name="reliability_read"),
    ),
    route_policy(
        name="spec_read",
        path="/api/spec",
        requirement=AccessRequirement(required=False, policy_name="spec_read"),
    ),
    route_policy(
        name="spec_read_v3",
        path="/v3/api/spec",
        requirement=AccessRequirement(required=False, policy_name="spec_read"),
    ),
    route_policy(
        name="public_artifacts_read",
        path="/api/public",
        requirement=AccessRequirement(required=False, policy_name="public_artifacts_read"),
    ),
    route_policy(
        name="public_artifacts_read_v3",
        path="/v3/api/public",
        requirement=AccessRequirement(required=False, policy_name="public_artifacts_read"),
    ),
    route_policy(
        name="experimental_read_v2",
        path="/v2/",
        requirement=AccessRequirement(required=True, policy_name="experimental_read", scope="commercial.read"),
        methods=("GET",),
    ),
    route_policy(
        name="experimental_read_v4",
        path="/v4/",
        requirement=AccessRequirement(required=True, policy_name="experimental_read", scope="commercial.read"),
        methods=("GET",),
    ),
    route_policy(
        name="experimental_read_v5",
        path="/v5/",
        requirement=AccessRequirement(required=True, policy_name="experimental_read", scope="commercial.read"),
        methods=("GET",),
    ),
    route_policy(
        name="experimental_write_v2",
        path="/v2/",
        requirement=AccessRequirement(required=True, policy_name="experimental_write", admin_only=True),
        methods=("POST", "PUT", "PATCH", "DELETE"),
    ),
    route_policy(
        name="experimental_write_v4",
        path="/v4/",
        requirement=AccessRequirement(required=True, policy_name="experimental_write", admin_only=True),
        methods=("POST", "PUT", "PATCH", "DELETE"),
    ),
    route_policy(
        name="experimental_write_v5",
        path="/v5/",
        requirement=AccessRequirement(required=True, policy_name="experimental_write", admin_only=True),
        methods=("POST", "PUT", "PATCH", "DELETE"),
    ),
)


def classify_request(path: str, method: str) -> AccessRequirement:
    if _is_public_path(path):
        return AccessRequirement(required=False, policy_name="public")

    if path.startswith(PROVENANCE_PREFIXES):
        if method.upper() != "GET":
            return AccessRequirement(required=True, policy_name="provenance_admin", admin_only=True)
        if any(path.startswith(prefix) for prefix in PROVENANCE_READ_PREFIXES):
            return AccessRequirement(required=False, policy_name="provenance_read")
        return AccessRequirement(required=True, policy_name="provenance_admin", admin_only=True)

    for policy in ROUTE_POLICY_REGISTRY:
        if policy.matches(path, method):
            return policy.requirement

    return AccessRequirement(required=False, policy_name="public")


def authenticate_request(request: Request, settings: AppSettings) -> Principal | None:
    auth_header = request.headers.get("authorization", "").strip()
    if auth_header.startswith("Bearer ") and settings.admin_token:
        candidate = auth_header.removeprefix("Bearer ").strip()
        if candidate and hmac.compare_digest(candidate, settings.admin_token):
            return Principal(
                principal_type="admin",
                principal_id="admin",
                scopes=frozenset({"ops.admin", "commercial.read"}),
            )

    api_key = request.headers.get("x-api-key", "").strip()
    if not api_key:
        return None

    for record in settings.api_keys.values():
        if hmac.compare_digest(api_key, record.secret):
            return Principal(
                principal_type="api_key",
                principal_id=record.key_id,
                scopes=record.scopes,
            )

    return None
