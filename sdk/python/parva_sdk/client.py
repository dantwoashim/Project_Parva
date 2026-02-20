"""Production-grade Python SDK client for Project Parva."""

from __future__ import annotations

import time
from datetime import date
from typing import Any, Callable, Dict, Optional

import httpx

from .exceptions import ParvaAPIError
from .models import DataEnvelope

RawResponse = Dict[str, Any]
RequestFn = Callable[..., RawResponse]


class ParvaClient:
    """
    Project Parva client with:
    - typed envelope responses
    - retry/backoff for transient failures
    - v3 public-profile defaults
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v3/api",
        timeout: int = 15,
        retries: int = 2,
        backoff_seconds: float = 0.3,
        request_fn: Optional[RequestFn] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = max(retries, 0)
        self.backoff_seconds = max(backoff_seconds, 0.0)
        self._request_fn = request_fn

    def _default_request(self, method: str, path: str, params: Optional[Dict[str, str]] = None) -> RawResponse:
        if method.upper() != "GET":  # SDK currently exposes GET-only endpoints.
            raise ValueError("ParvaClient currently supports GET requests only")

        last_exc: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                    response = client.request(method, path, params=params)
                if response.status_code >= 500 and attempt < self.retries:
                    time.sleep(self.backoff_seconds * (2 ** attempt))
                    continue
                if response.status_code < 200 or response.status_code >= 300:
                    raise ParvaAPIError(
                        response.status_code,
                        "non-success response",
                        body=response.text[:500],
                    )
                return response.json()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                if attempt >= self.retries:
                    raise
                time.sleep(self.backoff_seconds * (2 ** attempt))

        if last_exc:
            raise last_exc
        raise RuntimeError("Request failed without error detail")

    def _request(self, method: str, path: str, params: Optional[Dict[str, str]] = None) -> RawResponse:
        if self._request_fn:
            # Supports both legacy 3-arg and modern 4-arg injectors.
            try:
                return self._request_fn(method, path, params, self.timeout)
            except TypeError:
                return self._request_fn(method, path, params)
        return self._default_request(method, path, params)

    def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> DataEnvelope[RawResponse]:
        payload = self._request("GET", path, params)
        return DataEnvelope.from_dict(payload)

    def today(self) -> DataEnvelope[RawResponse]:
        return self._get("/calendar/today")

    def convert(self, value: str) -> DataEnvelope[RawResponse]:
        return self._get("/calendar/convert", {"date": value})

    def panchanga(self, value: Optional[str] = None) -> DataEnvelope[RawResponse]:
        target = value or date.today().isoformat()
        return self._get("/calendar/panchanga", {"date": target})

    def upcoming(self, days: int = 30) -> DataEnvelope[RawResponse]:
        return self._get("/festivals/upcoming", {"days": str(days)})

    def observances(self, value: str, location: str = "kathmandu", preferences: str = "") -> DataEnvelope[RawResponse]:
        params: Dict[str, str] = {"date": value, "location": location}
        if preferences:
            params["preferences"] = preferences
        return self._get("/observances", params)

    def explain_festival(self, festival_id: str, year: int) -> DataEnvelope[RawResponse]:
        return self._get(f"/festivals/{festival_id}/explain", {"year": str(year)})

    def explain_trace(self, trace_id: str) -> DataEnvelope[RawResponse]:
        return self._get(f"/explain/{trace_id}")

    def next_observance(
        self,
        from_date: Optional[str] = None,
        days: int = 30,
        location: str = "kathmandu",
        preferences: str = "",
    ) -> DataEnvelope[RawResponse]:
        params: Dict[str, str] = {"days": str(days), "location": location}
        if from_date:
            params["from_date"] = from_date
        if preferences:
            params["preferences"] = preferences
        return self._get("/observances/next", params)

    def resolve(
        self,
        value: str,
        profile: str = "np-mainstream",
        latitude: float = 27.7172,
        longitude: float = 85.3240,
        include_trace: bool = True,
    ) -> DataEnvelope[RawResponse]:
        params: Dict[str, str] = {
            "date": value,
            "profile": profile,
            "latitude": str(latitude),
            "longitude": str(longitude),
            "include_trace": "true" if include_trace else "false",
        }
        return self._get("/resolve", params)

    def spec_conformance(self) -> DataEnvelope[RawResponse]:
        return self._get("/spec/conformance")

    def verify_trace(self, trace_id: str) -> DataEnvelope[RawResponse]:
        return self._get(f"/provenance/verify/trace/{trace_id}")
