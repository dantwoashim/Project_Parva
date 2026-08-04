"""Public Future BS SDK helpers kept separate from the core v3 client surface."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import ParvaClient

JsonObject = dict[str, Any]
DEFAULT_FUTURE_BS_CAPABILITIES_URL = (
    "https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities"
)


def build_future_bs_url(capabilities_url: str, path: str) -> str:
    base = capabilities_url.rstrip("/")
    if base.endswith("/capabilities"):
        base = base[: -len("/capabilities")]
    return f"{base}/{path.lstrip('/')}"


def _client_or_default(client: ParvaClient | None) -> ParvaClient:
    if client is not None:
        return client
    from .client import ParvaClient

    return ParvaClient()


def get_future_bs_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return _client_or_default(client).get_future_bs_capabilities()


def get_future_bs_methodology(*, client: ParvaClient | None = None) -> JsonObject:
    return _client_or_default(client).get_future_bs_methodology()


def get_future_bs_forecast(
    bs_year: int,
    *,
    client: ParvaClient | None = None,
) -> JsonObject:
    return _client_or_default(client).get_future_bs_forecast(bs_year)


__all__ = [
    "DEFAULT_FUTURE_BS_CAPABILITIES_URL",
    "build_future_bs_url",
    "get_future_bs_capabilities",
    "get_future_bs_forecast",
    "get_future_bs_methodology",
]
