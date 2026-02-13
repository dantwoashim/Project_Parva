"""Engine metadata + plugin endpoints."""

from datetime import date
from fastapi import APIRouter
from fastapi import HTTPException, Query

from app.engine.ephemeris_config import get_ephemeris_config
from app.calendar.ephemeris.swiss_eph import get_ephemeris_info
from app.engine.plugins import get_plugin_registry
from app.rules.plugins import (
    ChineseObservancePlugin,
    HebrewObservancePlugin,
    IslamicObservancePlugin,
    NepaliHinduObservancePlugin,
    TibetanBuddhistObservancePlugin,
)

router = APIRouter(prefix="/api/engine", tags=["engine"])

_registry = get_plugin_registry()
_observance_plugins = {
    "nepali_hindu": NepaliHinduObservancePlugin(),
    "tibetan_buddhist": TibetanBuddhistObservancePlugin(),
    "islamic": IslamicObservancePlugin(),
    "hebrew": HebrewObservancePlugin(),
    "chinese": ChineseObservancePlugin(),
}


@router.get("/config")
async def get_engine_config():
    """Return current runtime engine configuration."""
    cfg = get_ephemeris_config()
    return {
        "ayanamsa": cfg.ayanamsa,
        "coordinate_system": cfg.coordinate_system,
        "ephemeris_mode": cfg.ephemeris_mode,
        "header": cfg.header_value,
    }


@router.get("/health")
async def get_engine_health():
    """Return ephemeris health/metadata."""
    cfg = get_ephemeris_config()
    info = get_ephemeris_info()
    return {
        "status": "ok",
        "ephemeris": info["mode"],
        "ayanamsa": cfg.ayanamsa,
        "coordinate_system": cfg.coordinate_system,
        "library": info.get("library", "pyswisseph"),
    }


@router.get("/calendars")
async def list_calendars():
    """List registered calendar plugins."""
    return {
        "calendars": [m.__dict__ for m in _registry.list_metadata()],
        "count": len(_registry.list_ids()),
    }


@router.get("/convert")
async def convert_with_plugin(
    date_str: str = Query(..., alias="date", description="Gregorian date YYYY-MM-DD"),
    calendar: str = Query("bs", description="Plugin id: bs|ns|tibetan|islamic|hebrew|chinese"),
):
    """Convert Gregorian date via selected calendar plugin."""
    try:
        year, month, day = [int(v) for v in date_str.split("-")]
        value = date(year, month, day)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD") from exc

    try:
        plugin = _registry.get(calendar)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    converted = plugin.convert_from_gregorian(value)
    return {
        "gregorian": value.isoformat(),
        "calendar": calendar,
        "result": converted.__dict__,
        "metadata": plugin.metadata().__dict__,
    }


@router.get("/observance-plugins")
async def list_observance_plugins():
    """List available observance plugins."""
    return {
        "plugins": sorted(_observance_plugins.keys()),
    }


def _calculate_observance_internal(
    *,
    plugin: str,
    rule_id: str,
    year: int,
    mode: str,
):
    if plugin not in _observance_plugins:
        raise HTTPException(status_code=404, detail=f"Unknown observance plugin: {plugin}")
    result = _observance_plugins[plugin].calculate(rule_id, year, mode=mode)
    if not result:
        raise HTTPException(status_code=404, detail=f"Rule not found or could not be calculated: {rule_id}")
    return {
        "plugin": plugin,
        "mode": mode,
        "result": result.__dict__,
    }


@router.get("/observance-calculate")
async def calculate_observance_v2(
    plugin: str = Query("nepali_hindu"),
    rule_id: str = Query(..., description="Rule/festival identifier"),
    year: int = Query(..., ge=2000, le=2200),
    mode: str = Query("computed", description="calculation mode: computed|tabular|astronomical|announced"),
):
    """Calculate one observance through selected observance plugin."""
    return _calculate_observance_internal(plugin=plugin, rule_id=rule_id, year=year, mode=mode)


@router.get("/observances")
async def calculate_observance(
    plugin: str = Query("nepali_hindu"),
    rule_id: str = Query(..., description="Rule/festival identifier"),
    year: int = Query(..., ge=2000, le=2200),
    mode: str = Query("computed", description="calculation mode: computed|tabular|astronomical|announced"),
):
    """Backward-compatible alias for observance plugin calculation."""
    return _calculate_observance_internal(plugin=plugin, rule_id=rule_id, year=year, mode=mode)
