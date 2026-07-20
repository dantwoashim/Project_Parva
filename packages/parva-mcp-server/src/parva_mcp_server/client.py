"""Bounded HTTP client for the public Project Parva agent gateway."""

from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.parse import urlsplit

import httpx

from .manifest import AGENT_GATEWAY_ROUTE, DEFAULT_PUBLIC_ORIGIN

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_TIMEOUT_SECONDS = 120.0
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
_SAFE_CODE_RE = re.compile(r"[^A-Z0-9_]")


class ParvaClientError(RuntimeError):
    """Safe, structured failure returned by the public API client."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int | None = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(_safe_message(message))
        self.code = _safe_code(code)
        self.status_code = status_code
        self.retryable = retryable

    def payload(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "code": self.code,
            "message": str(self),
            "retryable": self.retryable,
        }
        if self.status_code is not None:
            result["status_code"] = self.status_code
        return result


class ParvaPublicClient:
    """Call the single read-only Project Parva agent execution boundary."""

    def __init__(
        self,
        origin: str | None = None,
        *,
        timeout: float | None = None,
        max_response_bytes: int | None = None,
        token: str | None = None,
    ) -> None:
        self.origin = validate_public_origin(
            origin or os.getenv("PARVA_PUBLIC_ORIGIN") or DEFAULT_PUBLIC_ORIGIN
        )
        self.timeout = _bounded_float(
            timeout,
            env_name="PARVA_HTTP_TIMEOUT_SECONDS",
            default=DEFAULT_TIMEOUT_SECONDS,
            minimum=1.0,
            maximum=MAX_TIMEOUT_SECONDS,
        )
        self.max_response_bytes = _bounded_int(
            max_response_bytes,
            env_name="PARVA_MAX_RESPONSE_BYTES",
            default=DEFAULT_MAX_RESPONSE_BYTES,
            minimum=1024,
            maximum=MAX_RESPONSE_BYTES,
        )
        self.token = token if token is not None else os.getenv("PARVA_API_TOKEN", "").strip()

    def request(self, method: str, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        if method.upper() != "POST" or route != AGENT_GATEWAY_ROUTE:
            raise ParvaClientError(
                "The MCP adapter attempted to leave the public agent gateway.",
                code="UNSAFE_ROUTE",
            )
        if not isinstance(payload, dict):
            raise ParvaClientError("Request payload must be an object.", code="INVALID_REQUEST")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "parva-mcp-server/1",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        timeout = httpx.Timeout(
            timeout=self.timeout,
            connect=min(self.timeout, 10.0),
            read=self.timeout,
            write=min(self.timeout, 15.0),
            pool=min(self.timeout, 5.0),
        )
        try:
            with httpx.Client(
                timeout=timeout,
                follow_redirects=False,
                trust_env=False,
                limits=httpx.Limits(max_connections=4, max_keepalive_connections=2),
            ) as client:
                with client.stream(
                    "POST",
                    f"{self.origin}{AGENT_GATEWAY_ROUTE}",
                    headers=headers,
                    json=payload,
                ) as response:
                    raw = _read_bounded(response, self.max_response_bytes)
                    status_code = response.status_code
                    content_type = response.headers.get("content-type", "")
        except ParvaClientError:
            raise
        except httpx.TimeoutException as exc:
            raise ParvaClientError(
                "Project Parva did not respond before the configured timeout.",
                code="UPSTREAM_TIMEOUT",
                retryable=True,
            ) from exc
        except httpx.NetworkError as exc:
            raise ParvaClientError(
                "Project Parva is temporarily unreachable.",
                code="UPSTREAM_UNAVAILABLE",
                retryable=True,
            ) from exc
        except httpx.HTTPError as exc:
            raise ParvaClientError(
                "Project Parva could not complete the HTTP request.",
                code="UPSTREAM_HTTP_ERROR",
                retryable=True,
            ) from exc

        if 300 <= status_code < 400:
            raise ParvaClientError(
                "Project Parva returned a redirect, which the MCP adapter blocks.",
                code="UPSTREAM_REDIRECT_BLOCKED",
                status_code=status_code,
            )
        if status_code >= 400:
            decoded = _try_decode_json(raw)
            code, message = _extract_upstream_error(decoded, status_code)
            raise ParvaClientError(
                message,
                code=code,
                status_code=status_code,
                retryable=status_code in {408, 425, 429} or status_code >= 500,
            )
        if "application/json" not in content_type.lower():
            raise ParvaClientError(
                "Project Parva returned an unexpected content type.",
                code="INVALID_UPSTREAM_RESPONSE",
            )
        decoded = _decode_json(raw)
        if not isinstance(decoded, dict):
            raise ParvaClientError(
                "Project Parva returned a non-object JSON response.",
                code="INVALID_UPSTREAM_RESPONSE",
            )
        return decoded


def validate_public_origin(origin: str) -> str:
    parsed = urlsplit(str(origin or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("PARVA_PUBLIC_ORIGIN must be an absolute HTTP(S) origin")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("PARVA_PUBLIC_ORIGIN must not contain credentials, query, or fragment")
    if parsed.path not in {"", "/"}:
        raise ValueError("PARVA_PUBLIC_ORIGIN must not contain a path")
    hostname = parsed.hostname.lower()
    if parsed.scheme == "http" and hostname not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("PARVA_PUBLIC_ORIGIN must use HTTPS except for localhost")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _read_bounded(response: httpx.Response, maximum: int) -> bytes:
    declared = response.headers.get("content-length")
    if declared:
        try:
            if int(declared) > maximum:
                raise ParvaClientError(
                    "Project Parva returned a response larger than the configured limit.",
                    code="UPSTREAM_RESPONSE_TOO_LARGE",
                )
        except ValueError:
            pass
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_bytes():
        total += len(chunk)
        if total > maximum:
            raise ParvaClientError(
                "Project Parva returned a response larger than the configured limit.",
                code="UPSTREAM_RESPONSE_TOO_LARGE",
            )
        chunks.append(chunk)
    return b"".join(chunks)


def _decode_json(raw: bytes) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ParvaClientError(
            "Project Parva returned invalid JSON.",
            code="INVALID_UPSTREAM_RESPONSE",
        ) from exc


def _try_decode_json(raw: bytes) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def _extract_upstream_error(payload: Any, status_code: int) -> tuple[str, str]:
    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, dict):
        code = str(detail.get("code") or f"UPSTREAM_HTTP_{status_code}")
        message = str(detail.get("message") or "Project Parva rejected the tool input.")
        return _safe_code(code), _safe_message(message)
    if isinstance(detail, str):
        return f"UPSTREAM_HTTP_{status_code}", _safe_message(detail)
    return f"UPSTREAM_HTTP_{status_code}", "Project Parva could not execute the tool request."


def _safe_code(value: str) -> str:
    code = _SAFE_CODE_RE.sub("_", str(value).upper()).strip("_")
    return code[:80] or "MCP_TOOL_ERROR"


def _safe_message(value: str) -> str:
    text = " ".join(str(value).replace("\x00", "").split())
    return text[:400] or "Project Parva tool execution failed."


def _bounded_float(
    explicit: float | None,
    *,
    env_name: str,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    raw: Any = explicit if explicit is not None else os.getenv(env_name, str(default))
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{env_name} must be a number") from exc
    if value < minimum or value > maximum:
        raise ValueError(f"{env_name} must be between {minimum} and {maximum}")
    return value


def _bounded_int(
    explicit: int | None,
    *,
    env_name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    raw: Any = explicit if explicit is not None else os.getenv(env_name, str(default))
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{env_name} must be an integer") from exc
    if value < minimum or value > maximum:
        raise ValueError(f"{env_name} must be between {minimum} and {maximum}")
    return value


__all__ = ["ParvaClientError", "ParvaPublicClient", "validate_public_origin"]
