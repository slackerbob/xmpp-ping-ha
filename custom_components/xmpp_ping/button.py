"""Button that forces an immediate reachability check."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import XmppPingCoordinator
from .entity import XmppPingEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the "check now" button."""
    coordinator: XmppPingCoordinator = entry.runtime_data
    async_add_entities([XmppCheckNowButton(coordinator, entry)])


class XmppCheckNowButton(XmppPingEntity, ButtonEntity):
    """Pressing this runs a probe right away, off the normal schedule."""

    _attr_name = "Check now"

    def __init__(self, coordinator: XmppPingCoordinator, entry: ConfigEntry) -> None:
        """Create the force-check button."""
        super().__init__(coordinator, entry, key="check_now")

    async def async_press(self) -> None:
        """Trigger an on-demand probe via the coordinator."""
        await self.coordinator.async_request_refresh()
