"""Shared public API error payload helpers."""

from __future__ import annotations

from typing import Any

DEFAULT_API_VERSION = "3.0.0"


_STATUS_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "AUTHENTICATION_REQUIRED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    413: "REQUEST_TOO_LARGE",
    414: "QUERY_TOO_LONG",
    422: "REQUEST_VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_SERVER_ERROR",
}


def error_code_for_status(status_code: int) -> str:
    """Return a stable machine-readable error code for an HTTP status."""

    return _STATUS_ERROR_CODES.get(status_code, "HTTP_ERROR")


def _message_from_detail(detail: Any, default: str) -> str:
    if isinstance(detail, str) and detail:
        return detail
    if isinstance(detail, dict):
        for key in ("message", "detail", "error"):
            value = detail.get(key)
            if isinstance(value, str) and value:
                return value
    return default


def build_error_payload(
    *,
    status_code: int,
    detail: Any,
    request_id: str,
    version: str = DEFAULT_API_VERSION,
    code: str | None = None,
    details: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the public error envelope while preserving legacy fields.

    Existing clients historically consumed the top-level ``detail`` field. New
    clients can rely on ``error`` with a stable code, message, details object,
    and trace id.
    """

    default_message = "Internal Server Error" if status_code >= 500 else "Request failed"
    message = _message_from_detail(detail, default_message)
    error_details: dict[str, Any] = {}
    if isinstance(detail, dict) and isinstance(detail.get("details"), dict):
        error_details.update(detail["details"])
    if details:
        error_details.update(details)

    payload: dict[str, Any] = {
        "detail": detail,
        "request_id": request_id,
        "version": version,
        "error": {
            "code": code or error_code_for_status(status_code),
            "message": message,
            "details": error_details,
            "trace_id": request_id,
        },
    }
    if extra:
        payload.update(extra)
    return payload
