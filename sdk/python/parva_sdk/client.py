"""Production-grade Python SDK client for Project Parva."""

from __future__ import annotations

import inspect
import time
from datetime import date
from typing import Any, Callable, Dict, Optional

import httpx

from .exceptions import ParvaAPIError
from .models import DataEnvelope

RawResponse = Dict[str, Any]
RequestFn = Callable[..., RawResponse]
CoordinateValue = str | int | float | None


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

    def _default_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> RawResponse:
        last_exc: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                    response = client.request(method, path, params=params, json=json)
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

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> RawResponse:
        if self._request_fn:
            # Supports keyword-aware injectors first, then falls back to positional adapters.
            try:
                signature = inspect.signature(self._request_fn)
            except (TypeError, ValueError):
                signature = None

            if signature is not None:
                kwargs: Dict[str, Any] = {"method": method, "path": path}
                if "params" in signature.parameters:
                    kwargs["params"] = params
                if "json" in signature.parameters:
                    kwargs["json"] = json
                if "timeout" in signature.parameters:
                    kwargs["timeout"] = self.timeout
                try:
                    return self._request_fn(**kwargs)
                except TypeError:
                    kwargs = {}

            attempts: list[tuple[Any, ...]] = []
            if json is not None:
                attempts.extend(
                    [
                        (method, path, params, json, self.timeout),
                        (method, path, params, json),
                    ]
                )
            attempts.extend([(method, path, params, self.timeout), (method, path, params)])

            last_exc: Optional[TypeError] = None
            for attempt in attempts:
                try:
                    return self._request_fn(*attempt)
                except TypeError as exc:
                    last_exc = exc
                    continue

            if last_exc is not None:
                raise last_exc

            try:
                return self._request_fn(method, path, params)
            except TypeError:
                return self._request_fn(method, path)
        return self._default_request(method, path, params, json)

    def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> DataEnvelope[RawResponse]:
        payload = self._request("GET", path, params=params)
        return DataEnvelope.from_dict(payload)

    def _post(self, path: str, json: Optional[Dict[str, Any]] = None) -> DataEnvelope[RawResponse]:
        payload = self._request("POST", path, json=json)
        return DataEnvelope.from_dict(payload)

    @staticmethod
    def _normalize_coordinate(value: CoordinateValue) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        if isinstance(value, bool):
            return str(value).lower()
        return format(value, ".12g")

    @staticmethod
    def _normalize_optional_text(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    def _personal_payload(
        self,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: Optional[str] = None,
        **payload: Any,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        for key, value in payload.items():
            if value is None:
                continue
            if isinstance(value, str):
                stripped = value.strip()
                body[key] = stripped if stripped else value
                continue
            body[key] = value

        lat = self._normalize_coordinate(latitude)
        lon = self._normalize_coordinate(longitude)
        timezone_name = self._normalize_optional_text(tz)

        if lat is not None:
            body["lat"] = lat
        if lon is not None:
            body["lon"] = lon
        if timezone_name is not None:
            body["tz"] = timezone_name
        return body

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

    def temporal_compass(
        self,
        value: str,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
        quality_band: str = "computed",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/temporal/compass",
            self._personal_payload(
                date=value,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
                quality_band=quality_band,
            ),
        )

    def personal_panchanga(
        self,
        value: str,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/personal/panchanga",
            self._personal_payload(
                date=value,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
            ),
        )

    def muhurta_day(
        self,
        value: str,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
        birth_nakshatra: Optional[str] = None,
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/muhurta",
            self._personal_payload(
                date=value,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
                birth_nakshatra=self._normalize_optional_text(birth_nakshatra),
            ),
        )

    def rahu_kalam(
        self,
        value: str,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/muhurta/rahu-kalam",
            self._personal_payload(
                date=value,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
            ),
        )

    def auspicious_muhurta(
        self,
        value: str,
        *,
        ceremony_type: str = "general",
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
        birth_nakshatra: Optional[str] = None,
        assumption_set: str = "np-mainstream-v2",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/muhurta/auspicious",
            self._personal_payload(
                date=value,
                type=ceremony_type,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
                birth_nakshatra=self._normalize_optional_text(birth_nakshatra),
                assumption_set=assumption_set,
            ),
        )

    def muhurta_heatmap(
        self,
        value: str,
        *,
        ceremony_type: str = "general",
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
        assumption_set: str = "np-mainstream-v2",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/muhurta/heatmap",
            self._personal_payload(
                date=value,
                type=ceremony_type,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
                assumption_set=assumption_set,
            ),
        )

    def kundali(
        self,
        value: str,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/kundali",
            self._personal_payload(
                datetime=value,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
            ),
        )

    def kundali_lagna(
        self,
        value: str,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/kundali/lagna",
            self._personal_payload(
                datetime=value,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
            ),
        )

    def kundali_graph(
        self,
        value: str,
        *,
        latitude: CoordinateValue = None,
        longitude: CoordinateValue = None,
        tz: str = "Asia/Kathmandu",
    ) -> DataEnvelope[RawResponse]:
        return self._post(
            "/kundali/graph",
            self._personal_payload(
                datetime=value,
                latitude=latitude,
                longitude=longitude,
                tz=tz,
            ),
        )
