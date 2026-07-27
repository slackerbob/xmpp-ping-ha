"""Shared base entity for the XMPP Ping integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_info import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import XmppPingCoordinator


class XmppPingEntity(CoordinatorEntity[XmppPingCoordinator]):
    """Base entity: groups all three entities under one device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: XmppPingCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        """Wire the entity to the coordinator and set identity/device info."""
        super().__init__(coordinator)
        # Stable unique id per config entry + entity role.
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        # A single logical device so the three entities appear grouped.
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="XMPP Ping",
            model="Echo reachability monitor",
        )
