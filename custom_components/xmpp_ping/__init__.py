"""The XMPP Ping integration.

Sends a random token to a target JID and reports, via Home Assistant entities,
whether that same token is echoed back — a simple end-to-end reachability check
for an XMPP connection.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, Event, HomeAssistant

from .const import (
    CONF_HOST,
    CONF_JID,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_RETRY_INTERVAL_MINUTES,
    CONF_SCAN_INTERVAL_HOURS,
    CONF_TARGET_JID,
    CONF_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_RETRY_INTERVAL_MINUTES,
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
        retry_interval_minutes=_option(
            entry, CONF_RETRY_INTERVAL_MINUTES, DEFAULT_RETRY_INTERVAL_MINUTES
        ),
    )

    # Store the coordinator and set up the entity platforms.
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_first_probe(_event: Event | None = None) -> None:
        """Run the initial probe (in the background, never blocking setup)."""
        await coordinator.async_refresh()

    # A probe run during HA's boot often fails simply because networking, DNS,
    # or the remote server are not ready yet — which would then leave the status
    # "disconnected" until the next scheduled check. So when we are setting up
    # as part of startup, wait until HA has fully started before the first
    # probe. When the integration is (re)loaded at runtime, HA is already
    # running, so probe immediately. Either way, if that first probe still
    # fails, the coordinator's faster retry interval will recheck soon.
    if hass.state is CoreState.running:
        entry.async_create_background_task(
            hass, _async_first_probe(), f"{DOMAIN}_initial_probe"
        )
    else:
        entry.async_on_unload(
            hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, _async_first_probe
            )
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
