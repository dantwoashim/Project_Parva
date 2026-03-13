"""Route classification and authentication helpers."""

from __future__ import annotations

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
TRUST_PREFIXES = (
    "/api/reliability",
    "/v3/api/reliability",
    "/api/spec",
    "/v3/api/spec",
    "/api/public",
    "/v3/api/public",
)
WEBHOOK_PREFIXES = ("/api/webhooks", "/v3/api/webhooks")
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
    scope: str | None = None
    admin_only: bool = False


def _is_public_path(path: str) -> bool:
    if path in PUBLIC_HEALTH_PATHS:
        return True
    if path.startswith(("/assets/", "/favicon", "/manifest", "/sw.js")):
        return True
    return False


def classify_request(path: str, method: str) -> AccessRequirement:
    if _is_public_path(path):
        return AccessRequirement(required=False)

    if path.startswith(TRUST_PREFIXES):
        return AccessRequirement(required=True, scope="commercial.read")

    if path.startswith(WEBHOOK_PREFIXES):
        if path.endswith("/dispatch") or method.upper() != "GET":
            return AccessRequirement(required=True, admin_only=True)
        return AccessRequirement(required=True, scope="webhook.manage")

    if path.startswith(EXPERIMENTAL_PREFIXES):
        if method.upper() == "GET":
            return AccessRequirement(required=True, scope="commercial.read")
        return AccessRequirement(required=True, admin_only=True)

    if path.startswith(PROVENANCE_PREFIXES):
        if method.upper() != "GET":
            return AccessRequirement(required=True, admin_only=True)
        if any(path.startswith(prefix) for prefix in PROVENANCE_READ_PREFIXES):
            return AccessRequirement(required=True, scope="commercial.read")
        return AccessRequirement(required=True, admin_only=True)

    return AccessRequirement(required=False)


def authenticate_request(request: Request, settings: AppSettings) -> Principal | None:
    auth_header = request.headers.get("authorization", "").strip()
    if auth_header.startswith("Bearer ") and settings.admin_token:
        candidate = auth_header.removeprefix("Bearer ").strip()
        if candidate and candidate == settings.admin_token:
            return Principal(
                principal_type="admin",
                principal_id="admin",
                scopes=frozenset({"ops.admin", "commercial.read"}),
            )

    api_key = request.headers.get("x-api-key", "").strip()
    if not api_key:
        return None

    for record in settings.api_keys.values():
        if api_key == record.secret:
            return Principal(
                principal_type="api_key",
                principal_id=record.key_id,
                scopes=record.scopes,
            )

    return None
