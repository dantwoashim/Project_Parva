"""Deprecated compatibility import path for the Project Parva Python SDK."""

from __future__ import annotations

from warnings import warn

try:
    from parva_sdk import DataEnvelope, ParvaAPIError, ParvaClient, ParvaSDKError, ResponseMeta
except ImportError:  # pragma: no cover - repository import path fallback
    from ..parva_sdk import DataEnvelope, ParvaAPIError, ParvaClient, ParvaSDKError, ResponseMeta

warn(
    "The 'parva' package import path is deprecated; import from 'parva_sdk' instead.",
    DeprecationWarning,
    stacklevel=2,
)


class ParvaError(ParvaAPIError):
    """Deprecated alias for ParvaAPIError."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code, detail)


__all__ = [
    "ParvaClient",
    "ParvaSDKError",
    "ParvaAPIError",
    "ParvaError",
    "DataEnvelope",
    "ResponseMeta",
]
