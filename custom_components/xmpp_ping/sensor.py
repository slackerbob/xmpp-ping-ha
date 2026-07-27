"""Sensor exposing when the reachability check last ran."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_LAST_CHECKED
from .coordinator import XmppPingCoordinator
from .entity import XmppPingEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the "last checked" sensor."""
    coordinator: XmppPingCoordinator = entry.runtime_data
    async_add_entities([XmppLastCheckedSensor(coordinator, entry)])


class XmppLastCheckedSensor(XmppPingEntity, SensorEntity):
    """Timestamp of the most recent probe (successful or not)."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_name = "Last checked"

    def __init__(self, coordinator: XmppPingCoordinator, entry: ConfigEntry) -> None:
        """Create the last-checked sensor."""
        super().__init__(coordinator, entry, key="last_checked")

    @property
    def native_value(self) -> datetime | None:
        """Return the timestamp of the last probe, or None before the first."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(DATA_LAST_CHECKED)
