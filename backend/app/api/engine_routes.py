"""Engine metadata + plugin endpoints."""

from datetime import date
from pathlib import Path
from fastapi import APIRouter
from fastapi import HTTPException, Query

from app.engine.ephemeris_config import get_ephemeris_config
from app.calendar.ephemeris.swiss_eph import get_ephemeris_info
from app.engine.plugins import get_plugin_registry
from app.engine.plugins.validation import PluginValidationSuite
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

QUALITY_BAND_ORDER = {"provisional": 0, "beta": 1, "validated": 2, "gold": 3}

PLUGIN_QUALITY_PROFILES = {
    "bs": {"source_classes": ["official_table", "derived_model"], "error_budget": 0.0},
    "ns": {"source_classes": ["calendar_mapping", "derived_model"], "error_budget": 0.05},
    "tibetan": {"source_classes": ["plugin_formula", "published_calendar"], "error_budget": 0.1},
    "islamic": {"source_classes": ["tabular", "astronomical", "announced"], "error_budget": 0.15},
    "hebrew": {"source_classes": ["metonic_formula"], "error_budget": 0.05},
    "chinese": {"source_classes": ["lunisolar_formula"], "error_budget": 0.15},
    "julian": {"source_classes": ["julian_conversion"], "error_budget": 0.0},
}

STAGE1_VALIDATION_PLUGINS = {"bs", "ns", "tibetan", "islamic"}
STAGE2_VALIDATION_PLUGINS = {"hebrew", "chinese", "julian"}


def _plugin_validation_fixture_paths() -> list[Path]:
    root = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "plugins"
    return [
        root / "plugin_validation_cases.json",
        root / "plugin_validation_stage1_cases.json",
        root / "plugin_validation_stage2_cases.json",
    ]


def _quality_band_for_pass_rate(pass_rate: float, total: int) -> str:
    if total == 0:
        return "provisional"
    if pass_rate >= 99.0:
        return "gold"
    if pass_rate >= 95.0:
        return "validated"
    if pass_rate >= 80.0:
        return "beta"
    return "provisional"


def _lowest_quality_band(rows: list[dict]) -> str:
    if not rows:
        return "provisional"
    return min(
        (row.get("quality_band", "provisional") for row in rows),
        key=lambda band: QUALITY_BAND_ORDER.get(band, -1),
    )


def _plugin_quality_rows() -> list[dict]:
    case_totals: dict[str, int] = {}
    pass_totals: dict[str, int] = {}
    case_source_classes: dict[str, set[str]] = {}

    suite = PluginValidationSuite()
    for fixture_path in _plugin_validation_fixture_paths():
        if not fixture_path.exists():
            continue

        cases = suite.load_cases(fixture_path)
        report = suite.run(cases)
        for row in report.get("results", []):
            plugin = row.get("plugin")
            if not plugin:
                continue
            case_totals[plugin] = case_totals.get(plugin, 0) + 1
            if row.get("pass"):
                pass_totals[plugin] = pass_totals.get(plugin, 0) + 1

            source_class = row.get("source_class")
            if source_class:
                case_source_classes.setdefault(plugin, set()).add(source_class)

    rows: list[dict] = []
    for plugin_id in _registry.list_ids():
        total = case_totals.get(plugin_id, 0)
        passed = pass_totals.get(plugin_id, 0)
        pass_rate = round((passed / total) * 100, 2) if total else 0.0
        profile = PLUGIN_QUALITY_PROFILES.get(plugin_id, {})

        source_classes = set(profile.get("source_classes", ["undocumented"]))
        source_classes.update(case_source_classes.get(plugin_id, set()))

        error_budget = float(profile.get("error_budget", 0.2))
        observed_error_rate = round(max(0.0, 100.0 - pass_rate), 2)
        budget_rate = round(error_budget * 100.0, 2)
        rows.append({
            "plugin_id": plugin_id,
            "validation_cases_total": total,
            "pass_rate": pass_rate,
            "source_classes": sorted(source_classes),
            "error_budget": error_budget,
            "quality_band": _quality_band_for_pass_rate(pass_rate, total),
            "confidence_calibration": {
                "confidence_score": round(pass_rate / 100.0, 3),
                "observed_error_rate": observed_error_rate,
                "budget_error_rate": budget_rate,
                "within_error_budget": observed_error_rate <= budget_rate,
            },
        })

    return rows


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


@router.get("/plugins/quality")
async def plugin_quality():
    """Return quality parity metrics across all calendar plugins."""
    plugins = _plugin_quality_rows()
    validated_or_better = {"validated", "gold"}

    all_validated = all(row["quality_band"] in validated_or_better for row in plugins) if plugins else False
    rows_by_id = {row["plugin_id"]: row for row in plugins}

    stage1_rows = [rows_by_id[plugin_id] for plugin_id in sorted(STAGE1_VALIDATION_PLUGINS) if plugin_id in rows_by_id]
    stage1_validated = all(row["quality_band"] in validated_or_better for row in stage1_rows) if stage1_rows else False

    stage2_rows = [rows_by_id[plugin_id] for plugin_id in sorted(STAGE2_VALIDATION_PLUGINS) if plugin_id in rows_by_id]
    stage2_validated = all(row["quality_band"] in validated_or_better for row in stage2_rows) if stage2_rows else False

    all_within_error_budget = all(
        row.get("confidence_calibration", {}).get("within_error_budget", False)
        for row in plugins
    ) if plugins else False

    return {
        "plugins": plugins,
        "count": len(plugins),
        "stage1": {
            "target_plugins": sorted(STAGE1_VALIDATION_PLUGINS),
            "validated_plugins": [row["plugin_id"] for row in stage1_rows if row["quality_band"] in validated_or_better],
            "all_stage1_validated": stage1_validated,
        },
        "stage2": {
            "target_plugins": sorted(STAGE2_VALIDATION_PLUGINS),
            "validated_plugins": [row["plugin_id"] for row in stage2_rows if row["quality_band"] in validated_or_better],
            "all_stage2_validated": stage2_validated,
        },
        "global": {
            "all_plugins_validated": all_validated,
            "all_plugins_within_error_budget": all_within_error_budget,
            "sota_badge_allowed": all_validated and all_within_error_budget,
            "min_quality_band": _lowest_quality_band(plugins),
        },
    }


@router.get("/convert")
async def convert_with_plugin(
    date_str: str = Query(..., alias="date", description="Gregorian date YYYY-MM-DD"),
    calendar: str = Query("bs", description="Plugin id: bs|ns|tibetan|islamic|hebrew|chinese|julian"),
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
