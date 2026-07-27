"""Config flow (and options flow) for the XMPP Ping integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

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
)


class XmppPingConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup dialog."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect connection details from the user."""
        if user_input is not None:
            # One entry per (bot JID, target JID) pair.
            await self.async_set_unique_id(
                f"{user_input[CONF_JID]}::{user_input[CONF_TARGET_JID]}"
            )
            self._abort_if_unique_id_configured()
            title = f"{user_input[CONF_JID]} \u2192 {user_input[CONF_TARGET_JID]}"
            return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_JID): str,
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
                vol.Required(CONF_TARGET_JID): str,
                vol.Optional(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(
                    CONF_SCAN_INTERVAL_HOURS, default=DEFAULT_SCAN_INTERVAL_HOURS
                ): int,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> OptionsFlow:
        """Return the options flow handler."""
        return XmppPingOptionsFlow()


class XmppPingOptionsFlow(OptionsFlow):
    """Let the user tweak the interval and timeout without re-adding."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show and store the adjustable options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        data = self.config_entry.data
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL_HOURS,
                    default=options.get(
                        CONF_SCAN_INTERVAL_HOURS,
                        data.get(CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS),
                    ),
                ): int,
                vol.Optional(
                    CONF_TIMEOUT,
                    default=options.get(
                        CONF_TIMEOUT,
                        data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
                    ),
                ): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
