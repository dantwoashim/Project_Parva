"""Composable middleware for Project Parva app bootstrap."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.datastructures import Headers, QueryParams
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.bootstrap.access_control import authenticate_request, classify_request
from app.bootstrap.rate_limit import RateLimiterBackend, RatePolicy
from app.bootstrap.settings import AppSettings
from app.core.meta_envelope import extract_meta, merge_meta_defaults
from app.reliability.metrics import get_metrics_registry

logger = logging.getLogger("parva.request")
security_logger = logging.getLogger("parva.security")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
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
_ENVELOPE_PREFERENCE_HEADER = "X-Parva-Envelope"
_ENVELOPE_PREFERENCE_VALUE = "data-meta"
_ENVELOPE_PREFERENCE_ALIASES = {
    "1",
    "true",
    "yes",
    "on",
    "data-meta",
    "envelope",
    "full",
    "v1",
}


def _append_link_header(response: Response, value: str) -> None:
    existing = response.headers.get("Link")
    response.headers["Link"] = f"{existing}, {value}" if existing else value


def _append_vary_header(headers: dict[str, str], value: str) -> None:
    vary_key = next((key for key in headers if key.lower() == "vary"), "Vary")
    existing = headers.get(vary_key)
    if not existing:
        headers[vary_key] = value
        return

    entries = [item.strip() for item in existing.split(",") if item.strip()]
    if value.lower() not in {item.lower() for item in entries}:
        entries.append(value)
    headers[vary_key] = ", ".join(entries)


def parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _wants_data_meta_envelope(scope: Scope) -> bool:
    headers = Headers(raw=scope.get("headers", []))
    header_value = headers.get(_ENVELOPE_PREFERENCE_HEADER)
    query_params = QueryParams(scope.get("query_string", b"").decode("latin-1"))
    query_value = query_params.get("envelope")
    preference = header_value or query_value
    if preference is None:
        return False
    return preference.strip().lower() in _ENVELOPE_PREFERENCE_ALIASES


class RequestTooLargeError(Exception):
    """Internal signal to abort oversized streamed requests."""


def _headers_without_content_length(raw_headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
    filtered: dict[str, str] = {}
    for key, value in raw_headers:
        decoded_key = key.decode("latin-1")
        if decoded_key.lower() == "content-length":
            continue
        filtered[decoded_key] = value.decode("latin-1")
    return filtered


class RequestSizeGuardMiddleware:
    def __init__(self, app: ASGIApp, *, max_query_length: int, max_request_bytes: int) -> None:
        self.app = app
        self.max_query_length = max_query_length
        self.max_request_bytes = max_request_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if len(scope.get("query_string", b"")) > self.max_query_length:
            await JSONResponse(
                status_code=414, content={"detail": "Query string too long"}
            )(scope, receive, send)
            return

        headers = Headers(raw=scope.get("headers", []))
        content_length = headers.get("content-length")
        if content_length:
            try:
                declared_length = int(content_length)
            except ValueError:
                await JSONResponse(
                    status_code=400, content={"detail": "Invalid content-length header"}
                )(scope, receive, send)
                return

            if declared_length < 0:
                await JSONResponse(
                    status_code=400, content={"detail": "Invalid content-length header"}
                )(scope, receive, send)
                return

            if declared_length > self.max_request_bytes:
                await JSONResponse(
                    status_code=413, content={"detail": "Request payload too large"}
                )(scope, receive, send)
                return

        streamed_bytes = 0
        response_started = False

        async def guarded_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        async def guarded_receive() -> Message:
            nonlocal streamed_bytes
            message = await receive()
            if message["type"] != "http.request":
                return message

            body = message.get("body", b"")
            streamed_bytes += len(body)
            if streamed_bytes > self.max_request_bytes:
                raise RequestTooLargeError
            return message

        try:
            await self.app(scope, guarded_receive, guarded_send)
        except RequestTooLargeError:
            if response_started:
                raise
            await JSONResponse(
                status_code=413, content={"detail": "Request payload too large"}
            )(scope, receive, send)


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


def _log_security_event(
    *,
    event: str,
    request: Request,
    requirement_name: str,
    principal_id: str | None = None,
    reason: str | None = None,
) -> None:
    security_logger.info(
        json.dumps(
            {
                "event": event,
                "path": request.url.path,
                "method": request.method,
                "request_id": getattr(request.state, "request_id", None),
                "policy": requirement_name,
                "principal": principal_id,
                "reason": reason,
                "client_ip": getattr(request.state, "client_ip", None),
            }
        )
    )


def build_access_control_guard(*, settings: AppSettings):
    async def access_control(request: Request, call_next):
        requirement = classify_request(request.url.path, request.method)
        if not requirement.required:
            request.state.principal = None
            _log_security_event(
                event="auth.skipped",
                request=request,
                requirement_name=requirement.policy_name,
            )
            return await call_next(request)

        principal = authenticate_request(request, settings)
        if principal is None:
            reason = "credentials_missing"
            if request.headers.get("authorization") or request.headers.get("x-api-key"):
                reason = "credentials_invalid"
            _log_security_event(
                event="auth.denied",
                request=request,
                requirement_name=requirement.policy_name,
                reason=reason,
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Authentication required for this route",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        if requirement.admin_only and principal.principal_type != "admin":
            _log_security_event(
                event="auth.denied",
                request=request,
                requirement_name=requirement.policy_name,
                principal_id=principal.principal_id,
                reason="admin_required",
            )
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
            _log_security_event(
                event="auth.denied",
                request=request,
                requirement_name=requirement.policy_name,
                principal_id=principal.principal_id,
                reason=f"missing_scope:{requirement.scope}",
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": f"Missing required scope: {requirement.scope}",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

        request.state.principal = principal
        _log_security_event(
            event="auth.allowed",
            request=request,
            requirement_name=requirement.policy_name,
            principal_id=principal.principal_id,
        )
        return await call_next(request)

    return access_control


def _rate_policy_for_request(path: str, principal_type: str | None) -> tuple[str, RatePolicy]:
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


def build_rate_limit_guard(*, settings: AppSettings, backend: RateLimiterBackend):
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
        decision = backend.check(
            identifier=principal_id,
            bucket=bucket,
            policy=policy,
            now=time.time(),
        )

        if not decision.allowed:
            metrics.record_throttle(request.url.path)
            logger.warning(
                json.dumps(
                    {
                        "event": "request.throttled",
                        "request_id": getattr(request.state, "request_id", None),
                        "path": request.url.path,
                        "principal": principal_id,
                        "bucket": bucket,
                        "retry_after": decision.retry_after,
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
                    "Retry-After": str(decision.retry_after or policy.window_seconds),
                    "X-RateLimit-Limit": str(policy.limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(policy.limit)
        response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
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


class ExperimentalEnvelopeMiddleware:
    def __init__(self, app: ASGIApp, *, enable_experimental_api: bool) -> None:
        self.app = app
        self.enable_experimental_api = enable_experimental_api

    def _envelope_track(self, path: str, wants_v3_envelope: bool) -> str | None:
        is_v3 = path.startswith("/v3/api/") or path.startswith("/api/")
        is_v4 = path.startswith("/v4/api/")
        is_v5 = path.startswith("/v5/api/")
        if wants_v3_envelope and is_v3:
            return "v3"
        if self.enable_experimental_api and (is_v4 or is_v5):
            return "v5" if is_v5 else "v4"
        return None

    async def _forward_unmodified(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.app(scope, receive, send)

    def _build_envelope(self, payload: Any, *, track: str) -> dict[str, Any]:
        if isinstance(payload, dict) and "data" in payload and "meta" in payload:
            existing_meta = payload.get("meta")
            if not isinstance(existing_meta, dict):
                existing_meta = {}
            default_meta = extract_meta(payload.get("data"), track=track)
            return {
                "data": payload.get("data"),
                "meta": merge_meta_defaults(default_meta, existing_meta),
            }
        return {"data": payload, "meta": extract_meta(payload, track=track)}

    async def _send_wrapped_response(
        self,
        *,
        scope: Scope,
        receive: Receive,
        send: Send,
        response_start: Message,
        body: bytes,
        track: str,
    ) -> None:
        raw_headers = response_start.get("headers", [])
        headers = _headers_without_content_length(list(raw_headers))
        if track == "v3":
            _append_vary_header(headers, _ENVELOPE_PREFERENCE_HEADER)
            headers[_ENVELOPE_PREFERENCE_HEADER] = _ENVELOPE_PREFERENCE_VALUE
        media_type = Headers(raw=raw_headers).get("content-type")

        if not body:
            await Response(
                content=body,
                status_code=response_start["status"],
                media_type=media_type,
                headers=headers,
            )(scope, receive, send)
            return

        try:
            payload: Any = json.loads(body)
        except Exception:
            await Response(
                content=body,
                status_code=response_start["status"],
                media_type=media_type,
                headers=headers,
            )(scope, receive, send)
            return

        await JSONResponse(
            status_code=response_start["status"],
            content=self._build_envelope(payload, track=track),
            headers=headers,
        )(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._forward_unmodified(scope, receive, send)
            return

        path = scope.get("path", "")
        track = self._envelope_track(path, _wants_data_meta_envelope(scope))
        if track is None:
            await self._forward_unmodified(scope, receive, send)
            return

        response_start: Message | None = None
        body_buffer = bytearray()
        should_wrap = False

        async def send_wrapper(message: Message) -> None:
            nonlocal response_start, should_wrap
            if message["type"] == "http.response.start":
                headers = Headers(raw=message.get("headers", []))
                content_type = headers.get("content-type", "").lower()
                should_wrap = message["status"] < 400 and "application/json" in content_type
                if should_wrap:
                    response_start = message
                    return
                await send(message)
                return

            if message["type"] == "http.response.body" and should_wrap and response_start is not None:
                body_buffer.extend(message.get("body", b""))
                if message.get("more_body", False):
                    return

                await self._send_wrapped_response(
                    scope=scope,
                    receive=receive,
                    send=send,
                    response_start=response_start,
                    body=bytes(body_buffer),
                    track=track,
                )
                return

            await send(message)

        await self.app(scope, receive, send_wrapper)


def _engine_track_for_path(path: str) -> str:
    if path.startswith("/v2/"):
        return "v2"
    if path.startswith("/v4/"):
        return "v4"
    if path.startswith("/v5/"):
        return "v5"
    return "v3"


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
        response.headers["X-Parva-Engine"] = _engine_track_for_path(request.url.path)

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
