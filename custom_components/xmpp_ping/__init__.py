"""The XMPP Ping integration.

Sends a random token to a target JID and reports, via Home Assistant entities,
whether that same token is echoed back — a simple end-to-end reachability check
for an XMPP connection.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_HOST,
    CONF_JID,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL_HOURS,
    CONF_TARGET_JID,
    CONF_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DEFAULT_TIMEOUT,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import XmppPingCoordinator

# The coordinator is stored on the entry itself (modern runtime_data pattern).
type XmppPingConfigEntry = ConfigEntry[XmppPingCoordinator]


def _option(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Read a value from options first, then data, then fall back to default."""
    if key in entry.options:
        return entry.options[key]
    return entry.data.get(key, default)


async def async_setup_entry(hass: HomeAssistant, entry: XmppPingConfigEntry) -> bool:
    """Set up XMPP Ping from a config entry."""
    coordinator = XmppPingCoordinator(
        hass,
        jid=entry.data[CONF_JID],
        password=entry.data[CONF_PASSWORD],
        target_jid=entry.data[CONF_TARGET_JID],
        host=entry.data.get(CONF_HOST) or None,
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        timeout=_option(entry, CONF_TIMEOUT, DEFAULT_TIMEOUT),
        interval_hours=_option(entry, CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS),
    )

    # Store the coordinator and set up the entity platforms.
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Kick off the first probe in the background. A probe can take up to the
    # configured timeout, so we do not block setup on it — entities simply show
    # "unknown" until the first result lands.
    entry.async_create_background_task(
        hass, coordinator.async_refresh(), f"{DOMAIN}_initial_probe"
    )

    # Reload when the user changes options (e.g. a new interval or timeout).
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: XmppPingConfigEntry) -> bool:
    """Unload a config entry and its platforms."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: XmppPingConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
