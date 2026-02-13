"""Python SDK exceptions for Project Parva."""

from __future__ import annotations

from typing import Optional


class ParvaSDKError(RuntimeError):
    """Base SDK exception."""


class ParvaAPIError(ParvaSDKError):
    """Raised when the API returns a non-success response."""

    def __init__(self, status_code: int, message: str, *, body: Optional[str] = None):
        self.status_code = status_code
        self.message = message
        self.body = body
        details = f"Parva API {status_code}: {message}"
        if body:
            details = f"{details} | {body}"
        super().__init__(details)
