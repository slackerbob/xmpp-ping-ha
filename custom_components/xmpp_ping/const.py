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
CONF_RETRY_INTERVAL_MINUTES = "retry_interval_minutes"
CONF_TIMEOUT = "timeout"

# --- Defaults ---------------------------------------------------------------
DEFAULT_PORT = 5222
DEFAULT_SCAN_INTERVAL_HOURS = 12  # "twice a day"
DEFAULT_RETRY_INTERVAL_MINUTES = 20  # faster recheck while reachability is down
DEFAULT_TIMEOUT = 30  # seconds to wait for the echoed token

# The first probe after Home Assistant starts can catch the network, DNS, or
# the remote server before they are ready. Rather than wait a full retry
# interval, make a few quick attempts to ride out any brief boot-time gap.
STARTUP_PROBE_ATTEMPTS = 3
STARTUP_PROBE_RETRY_DELAY = 20  # seconds between those initial attempts

# Human-readable prefix put in front of the random token in the probe message,
# so it is recognisable in server/XMPP logs (e.g. "XMPP Ping test <token>").
PING_MESSAGE_PREFIX = "XMPP Ping test"

# --- Keys used inside the coordinator's data dict ---------------------------
DATA_CONNECTED = "connected"
DATA_LAST_CHECKED = "last_checked"

# Platforms this integration provides.
PLATFORMS = ["binary_sensor", "sensor", "button"]
