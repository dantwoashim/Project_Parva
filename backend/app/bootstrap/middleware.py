"""Composable middleware for Project Parva app bootstrap."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from app.core.meta_envelope import extract_meta, merge_meta_defaults


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
                    return JSONResponse(status_code=413, content={"detail": "Request payload too large"})
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid content-length header"})

        return await call_next(request)

    return request_size_guard


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
            existing_meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
            default_meta = extract_meta(payload.get("data"), track=track)
            merged_meta = merge_meta_defaults(default_meta, existing_meta)
            envelope = {"data": payload.get("data"), "meta": merged_meta}
        else:
            envelope = {"data": payload, "meta": extract_meta(payload, track=track)}

        headers = dict(response.headers)
        headers.pop("content-length", None)
        return JSONResponse(status_code=response.status_code, content=envelope, headers=headers)

    return envelope_adapter


def build_engine_headers(*, ephemeris_header_value: Callable[[], str], enable_experimental_api: bool):
    async def add_engine_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Parva-Ephemeris"] = ephemeris_header_value()

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

        if request.url.path.startswith("/api/"):
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = "Thu, 01 May 2027 00:00:00 GMT"
            response.headers["Link"] = "</v3/docs>; rel=\"successor-version\""

        if not enable_experimental_api and request.url.path.startswith(("/v2/", "/v4/", "/v5/")):
            # Should not happen due to gate, but keep explicit.
            response.headers["X-Parva-Experimental"] = "disabled"

        return response

    return add_engine_headers
