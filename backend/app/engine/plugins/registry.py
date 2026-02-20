"""Plugin registry for calendar conversion plugins."""

from __future__ import annotations

from datetime import date

from .base import CalendarDate, CalendarMetadata, CalendarPlugin
from .bikram_sambat.plugin import BikramSambatPlugin
from .chinese.plugin import ChineseCalendarPlugin
from .hebrew.plugin import HebrewCalendarPlugin
from .islamic.plugin import IslamicCalendarPlugin
from .julian_calendar.plugin import JulianCalendarPlugin
from .nepal_sambat.plugin import NepalSambatPlugin
from .tibetan.plugin import TibetanCalendarPlugin


class PluginRegistry:
    """In-memory plugin registry."""

    def __init__(self) -> None:
        self._plugins: dict[str, CalendarPlugin] = {}

    def register(self, plugin: CalendarPlugin) -> None:
        self._plugins[plugin.plugin_id] = plugin

    def get(self, plugin_id: str) -> CalendarPlugin:
        if plugin_id not in self._plugins:
            raise KeyError(f"Unknown plugin: {plugin_id}")
        return self._plugins[plugin_id]

    def list_metadata(self) -> list[CalendarMetadata]:
        return [plugin.metadata() for plugin in self._plugins.values()]

    def list_ids(self) -> list[str]:
        return sorted(self._plugins.keys())

    def convert(self, plugin_id: str, value: date) -> CalendarDate:
        plugin = self.get(plugin_id)
        return plugin.convert_from_gregorian(value)


_registry: PluginRegistry | None = None


def get_plugin_registry() -> PluginRegistry:
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
        _registry.register(BikramSambatPlugin())
        _registry.register(NepalSambatPlugin())
        _registry.register(TibetanCalendarPlugin())
        _registry.register(IslamicCalendarPlugin())
        _registry.register(HebrewCalendarPlugin())
        _registry.register(ChineseCalendarPlugin())
        _registry.register(JulianCalendarPlugin())
    return _registry
