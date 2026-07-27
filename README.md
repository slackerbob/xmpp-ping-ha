# XMPP Ping for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/slackerbob/hass-xmpp-ping)](https://github.com/slackerbob/hass-xmpp-ping/releases)
[![License](https://img.shields.io/github/license/slackerbob/hass-xmpp-ping)](LICENSE)

A Home Assistant integration that reports whether an XMPP connection can reach a
remote server. It periodically sends a **random one-time token** to a target
address and checks that the **exact same token** comes back. Anything that
isn't from that address, or whose body isn't the token, is ignored.

## Why

A plain "can I open a socket to the server" check tells you very little about
XMPP. Because this integration logs in and does a real message round-trip every
time, a green result means the **whole path** is healthy: your account login,
federation/routing out to the target's domain, and the remote responder — not
just that a port is open.

## Features

- 🟢 **Reachability binary sensor** (connectivity device class).
- 🕒 **"Last checked" timestamp sensor**.
- 🔘 **"Check now" button** to force a probe off-schedule.
- ⚙️ **UI config flow** — no YAML. Interval and timeout adjustable later.
- 🎯 **Strict matching** — only the exact token echoed from the exact target
  counts; everything else is ignored.
- 🔁 **Fresh login per probe**, so each check tests the full end-to-end path.

## Entities

All grouped under a single device:

| Entity | Type | Description |
| --- | --- | --- |
| `binary_sensor.<name>_reachable` | Binary sensor (connectivity) | `on` when the last probe was echoed back correctly, `off` when not, `unknown` before the first probe. |
| `sensor.<name>_last_checked` | Sensor (timestamp) | When the most recent probe ran (successful or not). |
| `button.<name>_check_now` | Button | Runs a probe immediately. |

## Installation

### HACS (recommended)

1. In HACS, open **⋮ → Custom repositories**.
2. Add `https://github.com/slackerbob/hass-xmpp-ping` with category
   **Integration**.
3. Install **XMPP Ping**, then restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**, search for
   **XMPP Ping**, and follow the dialog.

### Manual

1. Copy `custom_components/xmpp_ping/` into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the integration via **Settings → Devices & services → Add integration**.

## Configuration

Everything is entered through the UI when you add the integration.

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| Bot JID | Yes | — | The XMPP account to log in as, e.g. `bot@example.com`. |
| Password | Yes | — | Password for that account. |
| Target JID | Yes | — | The address to ping. Must run an echo responder (see below). |
| Server host | No | auto | Explicit server host. Leave blank to resolve via DNS SRV from the JID domain. |
| Server port | No | `5222` | XMPP client port. |
| Check interval (hours) | No | `12` | How often to probe. Default is twice a day. |
| Reply timeout (seconds) | No | `30` | How long to wait for the echo before declaring failure. |

Interval and timeout can be changed anytime via the integration's
**Configure** button.

## Prerequisite: an echo responder

The target JID must reflect back whatever it receives. If you don't already have
one, a few lines of [slixmpp](https://slixmpp.readthedocs.io/) do the job. Run
this as a small service on (or reachable through) the remote server you want to
monitor, using an account you control:

```python
"""Minimal XMPP echo bot for use with the XMPP Ping integration."""

from slixmpp import ClientXMPP


class EchoBot(ClientXMPP):
    def __init__(self, jid: str, password: str) -> None:
        super().__init__(jid, password)
        self.add_event_handler("session_start", self.on_start)
        self.add_event_handler("message", self.on_message)

    def on_start(self, _event) -> None:
        self.send_presence()
        self.get_roster()

    def on_message(self, msg) -> None:
        # Reflect direct chat messages straight back to the sender.
        if msg["type"] in ("chat", "normal"):
            msg.reply(msg["body"]).send()


if __name__ == "__main__":
    bot = EchoBot("echo@example.com", "password")
    bot.connect()
    bot.process(forever=True)
```

To genuinely test reaching a **specific remote server**, pick a target JID whose
domain lives on that server, so the probe message has to traverse it.

## How it works

Each probe is one complete cycle: **log in → send token → await echo →
disconnect**. A failed probe (auth failure, connection failure, timeout, or no
matching reply) is treated as valid data meaning *not reachable* rather than an
error — so the entities show a definite `off` state plus a fresh timestamp
instead of going `unavailable`.

## Troubleshooting

- **Always `off`.** Confirm the echo responder is running and that the target
  JID is exactly right. Test by messaging the target from a normal XMPP client
  and checking you get the same text back.
- **Slow first result.** The first probe runs in the background after setup and
  can take up to the reply timeout; entities read `unknown` until it completes.
- **Self-signed certificates.** TLS/STARTTLS with certificate verification is
  used by default. Verification cannot currently be disabled from the UI — open
  an issue if you need that toggle.
- **Logs.** Add the following to `configuration.yaml` for detail:

  ```yaml
  logger:
    logs:
      custom_components.xmpp_ping: debug
  ```

## Disclaimer

This is a community integration and is not affiliated with or endorsed by
Home Assistant or any XMPP server project.
