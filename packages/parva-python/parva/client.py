from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

DEFAULT_API_BASE = "https://api.prabinghimire1.com.np/v3/api"
DEFAULT_FUTURE_BS_CAPABILITIES_URL = (
    "https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities"
)

JsonObject = dict[str, Any]
Transport = Callable[[str, str, dict[str, str] | None, JsonObject | None, float], JsonObject]


class ParvaAPIError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


class ParvaNetworkError(RuntimeError):
    pass


@dataclass(frozen=True)
class BsDateInput:
    year: int
    month: int
    day: int


class ParvaClient:
    def __init__(
        self,
        base_url: str = DEFAULT_API_BASE,
        *,
        future_bs_capabilities_url: str = DEFAULT_FUTURE_BS_CAPABILITIES_URL,
        timeout: float = 10.0,
        transport: Transport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.future_bs_capabilities_url = future_bs_capabilities_url
        self.timeout = timeout
        self._transport = transport

    def get_today(self, risk_mode: str | None = None) -> JsonObject:
        params = {"risk_mode": risk_mode} if risk_mode else None
        return self._request("GET", "/calendar/today", params=params)

    def ad_to_bs(self, date: str) -> JsonObject:
        return self._request("GET", "/calendar/convert", params={"date": date})

    def bs_to_ad(self, year: int, month: int, day: int) -> JsonObject:
        return self._request(
            "POST",
            "/calendar/bs-to-gregorian",
            json_body={"year": year, "month": month, "day": day},
        )

    def validate_bs_date(self, year: int, month: int, day: int) -> JsonObject:
        try:
            payload = self.bs_to_ad(year, month, day)
        except ParvaAPIError as exc:
            if exc.status == 400:
                return {
                    "valid": False,
                    "publication_status": "computed_prediction_not_official",
                    "error": str(exc),
                }
            raise
        return {
            "valid": True,
            "publication_status": "computed_prediction_not_official",
            "result": payload,
        }

    def get_future_bs_capabilities(self) -> JsonObject:
        return self._request_absolute("GET", self.future_bs_capabilities_url)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json_body: JsonObject | None = None,
    ) -> JsonObject:
        url = _build_url(self.base_url, path, params)
        return self._request_absolute(method, url, json_body=json_body)

    def _request_absolute(
        self,
        method: str,
        url: str,
        *,
        json_body: JsonObject | None = None,
    ) -> JsonObject:
        if self._transport is not None:
            return self._transport(method, url, None, json_body, self.timeout)

        data = None
        headers = {"Accept": "application/json"}
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return _decode_response(response.read(), response.status)
        except urllib.error.HTTPError as exc:
            body = exc.read()
            parsed = _parse_json(body)
            detail = _extract_detail(parsed) or exc.reason
            raise ParvaAPIError(
                f"Parva API request failed with status {exc.code}: {detail}",
                status=exc.code,
                body=parsed,
            ) from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
            raise ParvaNetworkError(f"Parva API request failed: {exc}") from exc


def get_today(*, client: ParvaClient | None = None, risk_mode: str | None = None) -> JsonObject:
    return (client or ParvaClient()).get_today(risk_mode=risk_mode)


def ad_to_bs(date: str, *, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).ad_to_bs(date)


def bs_to_ad(
    year: int,
    month: int,
    day: int,
    *,
    client: ParvaClient | None = None,
) -> JsonObject:
    return (client or ParvaClient()).bs_to_ad(year, month, day)


def validate_bs_date(
    year: int,
    month: int,
    day: int,
    *,
    client: ParvaClient | None = None,
) -> JsonObject:
    return (client or ParvaClient()).validate_bs_date(year, month, day)


def get_future_bs_capabilities(*, client: ParvaClient | None = None) -> JsonObject:
    return (client or ParvaClient()).get_future_bs_capabilities()


def _build_url(base_url: str, path: str, params: dict[str, str] | None = None) -> str:
    normalized = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if not params:
        return normalized
    return f"{normalized}?{urllib.parse.urlencode(params)}"


def _decode_response(body: bytes, status: int) -> JsonObject:
    parsed = _parse_json(body)
    if not isinstance(parsed, dict):
        raise ParvaAPIError(
            "Parva API returned a non-object JSON payload",
            status=status,
            body=parsed,
        )
    return parsed


def _parse_json(body: bytes) -> Any:
    if not body:
        return {}
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def _extract_detail(payload: Any) -> str | None:
    if isinstance(payload, dict) and isinstance(payload.get("detail"), str):
        return payload["detail"]
    return None
