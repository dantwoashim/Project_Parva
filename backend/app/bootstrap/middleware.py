"""Composable middleware for Project Parva app bootstrap."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from app.bootstrap.access_control import WEBHOOK_PREFIXES, authenticate_request, classify_request
from app.bootstrap.settings import AppSettings
from app.core.meta_envelope import extract_meta, merge_meta_defaults
from app.reliability.metrics import get_metrics_registry

logger = logging.getLogger("parva.request")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


@dataclass(frozen=True)
class RatePolicy:
    limit: int
    window_seconds: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def check(
        self,
        *,
        identifier: str,
        bucket: str,
        policy: RatePolicy,
        now: float,
    ) -> tuple[bool, int, int | None]:
        bucket_key = (bucket, identifier)
        with self._lock:
            entries = self._buckets[bucket_key]
            cutoff = now - policy.window_seconds
            while entries and entries[0] <= cutoff:
                entries.popleft()

            if len(entries) >= policy.limit:
                retry_after = max(1, int(policy.window_seconds - (now - entries[0])))
                return False, 0, retry_after

            entries.append(now)
            remaining = max(policy.limit - len(entries), 0)
            return True, remaining, None


_rate_limiter = InMemoryRateLimiter()
_PRIVATE_RESPONSE_PREFIXES = (
    "/api/personal",
    "/v3/api/personal",
    "/api/muhurta",
    "/v3/api/muhurta",
    "/api/kundali",
    "/v3/api/kundali",
    "/api/temporal",
    "/v3/api/temporal",
)
_RATE_LIMITED_PREFIXES = (
    "/api",
    "/v2/api",
    "/v3/api",
    "/v4/api",
    "/v5/api",
)


def _append_link_header(response: Response, value: str) -> None:
    existing = response.headers.get("Link")
    response.headers["Link"] = f"{existing}, {value}" if existing else value


def parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def build_request_size_guard(*, max_query_length: int, max_request_bytes: int):
    async def request_size_guard(request: Request, call_next):
        if len(request.url.query) > max_query_length:
            return JSONResponse(status_code=414, content={"detail": "Query string too long"})

        cl = request.headers.get("content-length")
        if cl:
            try:
                if int(cl) > max_request_bytes:
                    return JSONResponse(
                        status_code=413, content={"detail": "Request payload too large"}
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400, content={"detail": "Invalid content-length header"}
                )

        if request.method.upper() in {"POST", "PUT", "PATCH"}:
            body = b""
            async for chunk in request.stream():
                if chunk:
                    body += chunk
                    if len(body) > max_request_bytes:
                        return JSONResponse(
                            status_code=413, content={"detail": "Request payload too large"}
                        )

            body_sent = False

            async def receive():
                nonlocal body_sent
                if body_sent:
                    return {"type": "http.request", "body": b"", "more_body": False}
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive
            request._body = body

        return await call_next(request)

    return request_size_guard


def _client_ip(request: Request, settings: AppSettings) -> str:
    remote_host = request.client.host if request.client and request.client.host else ""
    forwarded_for = request.headers.get("x-forwarded-for")
    trusted_proxy_ips = settings.trusted_proxy_ips
    trust_proxy_headers = "*" in trusted_proxy_ips or remote_host in trusted_proxy_ips
    if forwarded_for and trust_proxy_headers:
        forwarded_values = [value.strip() for value in forwarded_for.split(",") if value.strip()]
        if forwarded_values:
            return forwarded_values[0]
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def build_request_context(*, product_version: str, settings: AppSettings):
    metrics = get_metrics_registry()

    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id", "").strip() or uuid.uuid4().hex
        request.state.request_id = request_id
        request.state.client_ip = _client_ip(request, settings)
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
            logger.error(
                json.dumps(
                    {
                        "event": "request.error",
                        "request_id": request_id,
                        "path": request.url.path,
                        "method": request.method,
                        "latency_ms": latency_ms,
                        "version": product_version,
                    }
                )
            )
            raise

        latency_ms = round((time.perf_counter() - started) * 1000.0, 2)
        metrics.record_request(request.url.path, response.status_code, latency_ms)
        principal = getattr(request.state, "principal", None)
        logger.info(
            json.dumps(
                {
                    "event": "request.complete",
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "principal": getattr(principal, "principal_id", None),
                    "client_ip": request.state.client_ip,
                    "version": product_version,
                }
            )
        )
        response.headers["X-Request-ID"] = request_id
        return response

    return request_context


def build_access_control_guard(*, settings: AppSettings):
    async def access_control(request: Request, call_next):
        if request.url.path.startswith(WEBHOOK_PREFIXES) and not settings.enable_webhooks:
            return JSONResponse(
                status_code=404,
                content={
                    "detail": "Not Found",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        requirement = classify_request(request.url.path, request.method)
        if not requirement.required:
            request.state.principal = None
            return await call_next(request)

        principal = authenticate_request(request, settings)
        if principal is None:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Authentication required for this route",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        if requirement.admin_only and principal.principal_type != "admin":
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Admin token required for this route",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        if (
            requirement.scope
            and principal.principal_type != "admin"
            and not principal.has_scope(requirement.scope)
        ):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": f"Missing required scope: {requirement.scope}",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        request.state.principal = principal
        return await call_next(request)

    return access_control


def _rate_policy_for_request(path: str, principal_type: str | None) -> tuple[str, RatePolicy]:
    if path.startswith(("/api/webhooks", "/v3/api/webhooks")):
        return "webhooks", RatePolicy(limit=20, window_seconds=60)

    if path.startswith(
        (
            "/api/reliability",
            "/v3/api/reliability",
            "/api/spec",
            "/v3/api/spec",
            "/api/public",
            "/v3/api/public",
        )
    ):
        return "trusted", RatePolicy(limit=120, window_seconds=60)

    if path.startswith(
        (
            "/api/personal",
            "/v3/api/personal",
            "/api/muhurta",
            "/v3/api/muhurta",
            "/api/kundali",
            "/v3/api/kundali",
            "/api/resolve",
            "/v3/api/resolve",
            "/api/temporal",
            "/v3/api/temporal",
        )
    ):
        return "compute", RatePolicy(limit=40, window_seconds=60)

    if principal_type == "admin":
        return "admin", RatePolicy(limit=600, window_seconds=60)
    if principal_type:
        return "authenticated", RatePolicy(limit=240, window_seconds=60)
    return "public", RatePolicy(limit=120, window_seconds=60)


def _should_rate_limit(path: str) -> bool:
    return path.startswith(_RATE_LIMITED_PREFIXES)


def build_rate_limit_guard(*, settings: AppSettings):
    metrics = get_metrics_registry()

    async def rate_limit_guard(request: Request, call_next):
        if not settings.rate_limit_enabled or not _should_rate_limit(request.url.path):
            return await call_next(request)

        principal = getattr(request.state, "principal", None)
        principal_type = getattr(principal, "principal_type", None)
        principal_id = str(
            getattr(principal, "principal_id", "") or getattr(request.state, "client_ip", "unknown")
        )
        bucket, policy = _rate_policy_for_request(request.url.path, principal_type)
        allowed, remaining, retry_after = _rate_limiter.check(
            identifier=principal_id,
            bucket=bucket,
            policy=policy,
            now=time.time(),
        )

        if not allowed:
            metrics.record_throttle(request.url.path)
            logger.warning(
                json.dumps(
                    {
                        "event": "request.throttled",
                        "request_id": getattr(request.state, "request_id", None),
                        "path": request.url.path,
                        "principal": principal_id,
                        "bucket": bucket,
                        "retry_after": retry_after,
                    }
                )
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "request_id": getattr(request.state, "request_id", None),
                },
                headers={
                    "Retry-After": str(retry_after or policy.window_seconds),
                    "X-RateLimit-Limit": str(policy.limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(policy.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

    return rate_limit_guard


def build_experimental_version_gate(*, enable_experimental_api: bool):
    blocked_prefixes = ("/v2/api/", "/v4/api/", "/v5/api/")

    async def version_gate(request: Request, call_next):
        if not enable_experimental_api and request.url.path.startswith(blocked_prefixes):
            return JSONResponse(
                status_code=404,
                content={
                    "detail": "Endpoint unavailable in public profile. Use /v3/api/* or enable PARVA_ENABLE_EXPERIMENTAL_API.",
                    "public_profile": "v3",
                },
            )
        return await call_next(request)

    return version_gate


def build_envelope_adapter(*, enable_experimental_api: bool):
    async def envelope_adapter(request: Request, call_next):
        response = await call_next(request)

        if not enable_experimental_api:
            return response

        is_v4 = request.url.path.startswith("/v4/api/")
        is_v5 = request.url.path.startswith("/v5/api/")
        if not (is_v4 or is_v5):
            return response
        if response.status_code >= 400:
            return response

        content_type = response.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        if not body:
            return response

        try:
            payload: Any = json.loads(body)
        except Exception:
            headers = dict(response.headers)
            headers.pop("content-length", None)
            return Response(
                content=body,
                status_code=response.status_code,
                media_type=response.media_type,
                headers=headers,
            )

        track = "v5" if is_v5 else "v4"

        if isinstance(payload, dict) and "data" in payload and "meta" in payload:
            existing_meta = payload.get("meta")
            if not isinstance(existing_meta, dict):
                existing_meta = {}
            default_meta = extract_meta(payload.get("data"), track=track)
            merged_meta = merge_meta_defaults(default_meta, existing_meta)
            envelope = {"data": payload.get("data"), "meta": merged_meta}
        else:
            envelope = {"data": payload, "meta": extract_meta(payload, track=track)}

        headers = dict(response.headers)
        headers.pop("content-length", None)
        return JSONResponse(status_code=response.status_code, content=envelope, headers=headers)

    return envelope_adapter


def build_engine_headers(
    *,
    ephemeris_header_value: Callable[[], str],
    license_mode: str,
    source_url: str | None,
    enable_experimental_api: bool,
):
    async def add_engine_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Parva-Ephemeris"] = ephemeris_header_value()
        response.headers["X-Parva-License"] = license_mode

        if request.url.path.startswith("/v3/") or request.url.path.startswith("/api/"):
            response.headers["X-Parva-Engine"] = "v3"
        elif request.url.path.startswith("/v2/"):
            response.headers["X-Parva-Engine"] = "v2"
        elif request.url.path.startswith("/v4/"):
            response.headers["X-Parva-Engine"] = "v4"
        elif request.url.path.startswith("/v5/"):
            response.headers["X-Parva-Engine"] = "v5"
        else:
            response.headers["X-Parva-Engine"] = "v3"

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path.startswith(_PRIVATE_RESPONSE_PREFIXES):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"

        if source_url:
            _append_link_header(response, f'<{source_url}>; rel="source"')

        if request.url.path.startswith("/api/"):
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = "Thu, 01 May 2027 00:00:00 GMT"
            _append_link_header(response, '</v3/docs>; rel="successor-version"')

        if not enable_experimental_api and request.url.path.startswith(("/v2/", "/v4/", "/v5/")):
            # Should not happen due to gate, but keep explicit.
            response.headers["X-Parva-Experimental"] = "disabled"

        return response

    return add_engine_headers
