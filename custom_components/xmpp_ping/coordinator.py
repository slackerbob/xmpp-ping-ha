"""Data update coordinator for the XMPP Ping integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DATA_CONNECTED, DATA_LAST_CHECKED, DOMAIN
from .probe import XmppEchoProbe

_LOGGER = logging.getLogger(__name__)


class XmppPingCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Runs the echo probe on a schedule, and on demand from the button."""

    def __init__(
        self,
        hass: HomeAssistant,
        jid: str,
        password: str,
        target_jid: str,
        host: str | None,
        port: int,
        timeout: int,
        interval_hours: int,
    ) -> None:
        """Set up the coordinator with the probe parameters and interval."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=interval_hours),
        )
        self._jid = jid
        self._password = password
        self._target_jid = target_jid
        self._host = host
        self._port = port
        self._timeout = timeout

    async def _async_update_data(self) -> dict[str, Any]:
        """Run one probe.

        A failed probe is *valid data* meaning "not reachable" rather than an
        update error, so we never raise UpdateFailed here. That keeps the
        entities showing a definite off/on state plus a fresh timestamp instead
        of going unavailable.
        """
        probe = XmppEchoProbe(
            self._jid,
            self._password,
            self._target_jid,
            host=self._host,
            port=self._port,
            timeout=self._timeout,
        )
        connected = await probe.async_run()
        _LOGGER.debug("XMPP ping result: connected=%s", connected)
        return {
            DATA_CONNECTED: connected,
            DATA_LAST_CHECKED: dt_util.utcnow(),
        }
