"""Binary sensor reflecting whether the XMPP echo round-trip succeeded."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_CONNECTED
from .coordinator import XmppPingCoordinator
from .entity import XmppPingEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the reachability binary sensor."""
    coordinator: XmppPingCoordinator = entry.runtime_data
    async_add_entities([XmppReachableBinarySensor(coordinator, entry)])


class XmppReachableBinarySensor(XmppPingEntity, BinarySensorEntity):
    """On when the last probe was echoed back correctly."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_name = "Reachable"

    def __init__(self, coordinator: XmppPingCoordinator, entry: ConfigEntry) -> None:
        """Create the reachability sensor."""
        super().__init__(coordinator, entry, key="reachable")

    @property
    def is_on(self) -> bool | None:
        """Return True if reachable, False if not, None before the first probe."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(DATA_CONNECTED)
