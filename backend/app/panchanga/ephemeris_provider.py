"""Method-docketed ephemeris providers for Panchanga proof replay."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from app.calendar.ephemeris.swiss_eph import (
    calculate_sunrise,
    calculate_sunset,
    get_ephemeris_info,
)
from app.calendar.panchanga import get_panchanga
from app.panchanga.spk_kernel import validate_planetary_spk
from app.sources.hashing import canonical_json_hash

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = PROJECT_ROOT / "data" / "ephemeris" / "fixtures"


class EphemerisProvider(Protocol):
    @property
    def provider_id(self) -> str:
        """Stable provider identifier."""

    @property
    def provider_kind(self) -> str:
        """Provider class used in proof metadata."""

    def metadata(self) -> dict[str, Any]:
        """Return replay-relevant provider metadata."""

    def panchanga_for(
        self,
        target_date: date,
        *,
        latitude: float,
        longitude: float,
        timezone_name: str,
        ayanamsa: str,
    ) -> dict[str, Any]:
        """Compute or load Panchanga values for a specific location/date."""


def _sha256_json_file(path: Path) -> str:
    """Hash JSON fixtures by canonical content so replay survives checkout EOLs."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return f"sha256:{canonical_json_hash(payload)}"


def method_dockets() -> list[dict[str, Any]]:
    """Return deterministic method dockets for Panchanga computation."""

    return [
        {
            "method_id": "parva.panchanga.sunrise.v1",
            "algorithm": "Swiss Ephemeris sunrise calculation through pyswisseph",
            "implementation_version": "1.0.0",
            "precision_tolerance": "provider-dependent; fixture replay exact for pinned values",
            "time_standard": "UTC instant with observer IANA timezone projection",
            "coordinate_frame": "geocentric apparent ecliptic longitudes where applicable",
            "assumptions": ["observer latitude/longitude explicit", "sunrise attribution rule explicit"],
            "limitations": ["computed_not_official", "not_panchanga_authority", "not_ritual_final_authority"],
        },
        {
            "method_id": "parva.panchanga.tithi.v1",
            "algorithm": "floor((moon_sidereal_longitude - sun_sidereal_longitude) mod 360 / 12) + 1 at sunrise",
            "implementation_version": "1.0.0",
            "precision_tolerance": "depends on ephemeris provider and ayanamsa",
            "time_standard": "sunrise UTC instant",
            "coordinate_frame": "sidereal ecliptic longitude",
            "assumptions": ["Lahiri/chosen ayanamsa", "udaya tithi"],
            "limitations": ["computed_not_official", "not_ritual_final_authority"],
        },
        {
            "method_id": "parva.panchanga.nakshatra.v1",
            "algorithm": "floor(moon_sidereal_longitude / (360 / 27)) + 1 at sunrise",
            "implementation_version": "1.0.0",
            "precision_tolerance": "depends on ephemeris provider and ayanamsa",
            "time_standard": "sunrise UTC instant",
            "coordinate_frame": "sidereal ecliptic longitude",
            "assumptions": ["27 equal nakshatra divisions"],
            "limitations": ["computed_not_official", "not_ritual_final_authority"],
        },
        {
            "method_id": "parva.panchanga.yoga_karana.v1",
            "algorithm": "standard equal-division yoga and half-tithi karana calculations",
            "implementation_version": "1.0.0",
            "precision_tolerance": "depends on ephemeris provider and ayanamsa",
            "time_standard": "sunrise UTC instant",
            "coordinate_frame": "sidereal ecliptic longitude",
            "assumptions": ["computed components are decision support only"],
            "limitations": ["computed_not_official", "not_panchanga_authority"],
        },
    ]


@dataclass(frozen=True)
class BuiltInApproxProvider:
    """Built-in Swiss/Moshier provider used when no external kernel is configured."""

    provider_id: str = "builtin_swiss_moshier"
    provider_kind: str = "fallback_approximation"
    ephemeris_name: str = "Swiss Ephemeris built-in Moshier"
    ephemeris_version: str = "pyswisseph_builtin"

    def metadata(self) -> dict[str, Any]:
        info = get_ephemeris_info()
        return {
            "provider_id": self.provider_id,
            "provider_kind": self.provider_kind,
            "ephemeris_name": self.ephemeris_name,
            "ephemeris_version": self.ephemeris_version,
            "kernel_hash": None,
            "time_scale": "UTC",
            "coordinate_frame": info.get("coordinate_system", "sidereal"),
            "precision_tolerance": info.get("accuracy", "arcsecond"),
            "supported_date_range": "pyswisseph builtin range",
            "source_or_method_docket": "parva.panchanga.method_dockets.v1",
            "boundary_vector": {
                "claim_boundary": "computed_ephemeris_not_panchanga_authority",
                "not_authority": True,
                "review_required": True,
            },
            "fallback_used": True,
            "jpl_backed": False,
        }

    def panchanga_for(
        self,
        target_date: date,
        *,
        latitude: float,
        longitude: float,
        timezone_name: str,
        ayanamsa: str,
    ) -> dict[str, Any]:
        del ayanamsa
        return get_panchanga(target_date, latitude=latitude, longitude=longitude, timezone_name=timezone_name)


@dataclass(frozen=True)
class FixtureEphemerisProvider:
    """Pinned deterministic fixture provider for local replay tests."""

    fixture_id: str
    provider_id: str = "pinned_panchanga_fixture"
    provider_kind: str = "pinned_fixture"

    @property
    def fixture_path(self) -> Path:
        return FIXTURE_ROOT / f"{self.fixture_id}.json"

    def _payload(self) -> dict[str, Any]:
        return json.loads(self.fixture_path.read_text(encoding="utf-8"))

    def metadata(self) -> dict[str, Any]:
        payload = self._payload()
        return {
            "provider_id": self.provider_id,
            "provider_kind": self.provider_kind,
            "fixture_id": self.fixture_id,
            "ephemeris_name": payload.get("ephemeris_name", "pinned fixture slice"),
            "ephemeris_version": payload.get("ephemeris_version", "fixture-v1"),
            "kernel_hash": _sha256_json_file(self.fixture_path),
            "time_scale": payload.get("time_scale", "UTC"),
            "coordinate_frame": payload.get("coordinate_frame", "sidereal"),
            "precision_tolerance": payload.get("precision_tolerance", "exact pinned fixture replay"),
            "supported_date_range": payload.get("supported_date_range", "fixture dates only"),
            "source_or_method_docket": "parva.panchanga.method_dockets.v1",
            "boundary_vector": {
                "claim_boundary": "pinned_fixture_not_official_panchanga_authority",
                "not_authority": True,
                "review_required": True,
            },
            "fallback_used": False,
            "jpl_backed": bool(payload.get("jpl_fixture", False)),
        }

    def panchanga_for(
        self,
        target_date: date,
        *,
        latitude: float,
        longitude: float,
        timezone_name: str,
        ayanamsa: str,
    ) -> dict[str, Any]:
        payload = self._payload()
        expected = payload["query"]
        requested = {
            "date": target_date.isoformat(),
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "timezone": timezone_name.lower(),
            "ayanamsa": ayanamsa,
        }
        expected = {**expected, "timezone": str(expected.get("timezone")).lower()}
        if requested != expected:
            raise ValueError(f"fixture query mismatch: expected {expected}, got {requested}")
        return payload["panchanga"]


@dataclass(frozen=True)
class JplKernelMetadataProvider:
    """Validated JPL kernel metadata without a calculation-provider claim."""

    kernel_path: str | None = None
    provider_id: str = "jpl_de440_kernel_metadata"
    provider_kind: str = "verified_kernel_metadata_only"
    ephemeris_name: str = "JPL DE440-family SPK metadata"
    ephemeris_version: str = "de440"

    def _kernel(self) -> Path:
        configured = self.kernel_path or os.getenv("PARVA_JPL_KERNEL_PATH") or os.getenv("PARVA_JPL_DE440_KERNEL")
        if not configured:
            raise FileNotFoundError("PARVA_JPL_KERNEL_PATH/PARVA_JPL_DE440_KERNEL is not configured")
        path = Path(configured).expanduser()
        if not path.exists():
            raise FileNotFoundError("configured JPL kernel does not exist")
        return path

    def _validated_kernel(self, kernel: Path) -> tuple[str, int]:
        expected = os.getenv("PARVA_JPL_KERNEL_SHA256", "").strip()
        if not expected:
            raise ValueError("PARVA_JPL_KERNEL_SHA256 is required for a configured JPL kernel")
        configured_size = os.getenv("PARVA_JPL_KERNEL_SIZE", "").strip()
        expected_size = int(configured_size) if configured_size else None
        inventory = validate_planetary_spk(
            kernel,
            expected_sha256=expected,
            expected_size=expected_size,
        )
        normalized_hash = expected.lower().removeprefix("sha256:")
        return f"sha256:{normalized_hash}", len(inventory.segments)

    def metadata(self) -> dict[str, Any]:
        try:
            kernel = self._kernel()
        except FileNotFoundError:
            return {
                "provider_id": self.provider_id,
                "provider_kind": self.provider_kind,
                "ephemeris_name": self.ephemeris_name,
                "ephemeris_version": self.ephemeris_version,
                "kernel_hash": None,
                "available": False,
                "calculation_available": False,
                "jpl_backed": False,
                "boundary_vector": {
                    "claim_boundary": "jpl_kernel_metadata_unavailable_not_used",
                    "not_authority": True,
                    "review_required": True,
                },
            }
        kernel_hash, segment_count = self._validated_kernel(kernel)
        return {
            "provider_id": self.provider_id,
            "provider_kind": self.provider_kind,
            "ephemeris_name": self.ephemeris_name,
            "ephemeris_version": self.ephemeris_version,
            "kernel_hash": kernel_hash,
            "kernel_file": kernel.name,
            "segment_count": segment_count,
            "source_or_method_docket": "parva.panchanga.method_dockets.v1",
            "boundary_vector": {
                "claim_boundary": "verified_kernel_metadata_not_calculation_output",
                "not_authority": True,
                "review_required": True,
            },
            "available": True,
            "calculation_available": False,
            "jpl_backed": False,
        }

    def panchanga_for(
        self,
        target_date: date,
        *,
        latitude: float,
        longitude: float,
        timezone_name: str,
        ayanamsa: str,
    ) -> dict[str, Any]:
        del target_date, latitude, longitude, timezone_name, ayanamsa
        raise ValueError(
            "JPL DE440 is registered as verified kernel metadata only; "
            "no JPL Panchanga calculation provider is available"
        )


# Compatibility import for integrations that previously inspected kernel metadata.
JplEphemerisProvider = JplKernelMetadataProvider


def provider_from_id(provider_id: str, *, fixture_id: str | None = None) -> EphemerisProvider:
    normalized = provider_id.strip().lower()
    if normalized in {"builtin_swiss_moshier", "builtin", "fallback"}:
        return BuiltInApproxProvider()
    if normalized in {"pinned_panchanga_fixture", "fixture"}:
        if not fixture_id:
            raise ValueError("fixture provider requires fixture_id")
        return FixtureEphemerisProvider(fixture_id=fixture_id)
    if normalized in {"jpl_de440", "jpl"}:
        raise ValueError(
            "jpl_de440 cannot be selected for Panchanga calculations; "
            "only verified kernel metadata is implemented"
        )
    raise ValueError(f"unsupported ephemeris provider: {provider_id}")


def sunrise_payload(
    target_date: date,
    *,
    latitude: float,
    longitude: float,
    timezone_name: str,
) -> dict[str, Any]:
    sunrise = calculate_sunrise(target_date, latitude, longitude, timezone_name=timezone_name)
    sunset = calculate_sunset(target_date, latitude, longitude, timezone_name=timezone_name)
    return {
        "sunrise_utc": sunrise.astimezone(timezone.utc).isoformat(),
        "sunset_utc": sunset.astimezone(timezone.utc).isoformat(),
        "calculated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


__all__ = [
    "BuiltInApproxProvider",
    "EphemerisProvider",
    "FixtureEphemerisProvider",
    "JplEphemerisProvider",
    "JplKernelMetadataProvider",
    "method_dockets",
    "provider_from_id",
    "sunrise_payload",
]
