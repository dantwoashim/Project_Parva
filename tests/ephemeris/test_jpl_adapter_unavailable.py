from __future__ import annotations

import json

import pytest
from app.research.future_bs.ephemeris.base import EphemerisUnavailableError
from app.research.future_bs.ephemeris.jpl_spice_adapter import JPLSpiceAdapter


def test_missing_jpl_kernel_reports_unavailable_without_path_leak(tmp_path) -> None:
    missing = tmp_path / "missing.bsp"
    adapter = JPLSpiceAdapter(kernel_path=str(missing))

    assert adapter.available is False
    assert str(tmp_path) not in adapter.notes
    with pytest.raises(EphemerisUnavailableError) as exc:
        adapter.apparent_solar_longitude(2460400.5)
    assert str(tmp_path) not in str(exc.value)


def test_adapter_status_is_machine_readable_when_absent(tmp_path) -> None:
    adapter = JPLSpiceAdapter(kernel_path=str(tmp_path / "missing.bsp"))
    payload = adapter.status()

    assert payload["available"] is False
    assert payload["name"] == "jpl_spice_de440"
    assert str(tmp_path) not in json.dumps(payload)
