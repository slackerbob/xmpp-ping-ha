"""Constants for the XMPP Ping integration."""

from __future__ import annotations

DOMAIN = "xmpp_ping"

# --- Config / option keys ---------------------------------------------------
CONF_JID = "jid"
CONF_PASSWORD = "password"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_TARGET_JID = "target_jid"
CONF_SCAN_INTERVAL_HOURS = "scan_interval_hours"
CONF_TIMEOUT = "timeout"

# --- Defaults ---------------------------------------------------------------
DEFAULT_PORT = 5222
DEFAULT_SCAN_INTERVAL_HOURS = 12  # "twice a day"
DEFAULT_TIMEOUT = 30  # seconds to wait for the echoed token

# Human-readable prefix put in front of the random token in the probe message,
# so it is recognisable in server/XMPP logs (e.g. "XMPP Ping test <token>").
PING_MESSAGE_PREFIX = "XMPP Ping test"

# --- Keys used inside the coordinator's data dict ---------------------------
DATA_CONNECTED = "connected"
DATA_LAST_CHECKED = "last_checked"

# Platforms this integration provides.
PLATFORMS = ["binary_sensor", "sensor", "button"]
