"""A single XMPP echo probe.

The probe logs in, sends a short descriptive message containing a random
one-time token to the target JID, and waits for that *exact* message to come
back from that *exact* address. Anything that does not match (wrong sender,
wrong body, presence, other chats) is ignored.
The connection is torn down again afterwards so every probe is a fresh,
end-to-end test of: local login -> federation/routing -> remote responder.
"""

from __future__ import annotations

import asyncio
import logging
import uuid

from slixmpp import ClientXMPP
from slixmpp.jid import JID

from .const import PING_MESSAGE_PREFIX

_LOGGER = logging.getLogger(__name__)


class XmppEchoProbe:
    """Perform a single connect -> send -> await-echo -> disconnect cycle."""

    def __init__(
        self,
        jid: str,
        password: str,
        target_jid: str,
        host: str | None = None,
        port: int = 5222,
        timeout: int = 30,
    ) -> None:
        """Store the parameters for one probe run."""
        self._jid = jid
        self._password = password
        self._target_jid = target_jid
        self._host = host
        self._port = port
        self._timeout = timeout

    async def async_run(self) -> bool:
        """Run one probe.

        Returns True only if the precise token we generated is echoed back by
        the target address within the timeout. Every other outcome (auth
        failure, connection failure, timeout, unexpected message) yields False.
        """
        # A random, single-use token so we can be certain the reply is *ours*.
        token = uuid.uuid4().hex
        # The full message body sent (and expected back): a readable prefix plus
        # the token, so it is easy to spot in XMPP/server logs.
        payload = f"{PING_MESSAGE_PREFIX} {token}"
        loop = asyncio.get_running_loop()
        result: asyncio.Future[bool] = loop.create_future()

        xmpp = ClientXMPP(self._jid, self._password)
        target_bare = JID(self._target_jid).bare

        def _resolve(value: bool) -> None:
            # Only the first outcome counts; later events are ignored.
            if not result.done():
                result.set_result(value)

        def on_session_start(_event) -> None:
            # We are authenticated and bound; fire the probe message.
            xmpp.send_presence()
            xmpp.send_message(mto=self._target_jid, mbody=payload, mtype="chat")
            _LOGGER.debug("Sent XMPP echo payload to %s", self._target_jid)

        def on_message(msg) -> None:
            # Ignore anything that is not from the exact address we pinged.
            if JID(msg["from"]).bare != target_bare:
                return
            # Ignore anything whose body is not the exact payload we sent.
            if msg["body"] != payload:
                return
            _LOGGER.debug("Received matching echo from %s", msg["from"])
            _resolve(True)

        def on_failure(_event=None) -> None:
            # Auth or transport failure means the connection is not healthy.
            _resolve(False)

        xmpp.add_event_handler("session_start", on_session_start)
        xmpp.add_event_handler("message", on_message)
        xmpp.add_event_handler("failed_auth", on_failure)
        xmpp.add_event_handler("connection_failed", on_failure)

        try:
            # If a host is given we connect there explicitly, otherwise slixmpp
            # resolves the domain from the JID via DNS SRV records.
            if self._host:
                xmpp.connect(address=(self._host, self._port))
            else:
                xmpp.connect()
            return await asyncio.wait_for(result, timeout=self._timeout)
        except asyncio.TimeoutError:
            _LOGGER.debug("XMPP echo timed out after %s s", self._timeout)
            return False
        except Exception:  # noqa: BLE001 - any failure means "not reachable"
            _LOGGER.exception("XMPP echo probe raised an unexpected error")
            return False
        finally:
            await self._async_disconnect(xmpp)

    @staticmethod
    async def _async_disconnect(xmpp: ClientXMPP) -> None:
        """Tear the connection down cleanly across slixmpp versions."""
        try:
            # Depending on the slixmpp version, disconnect() may be a coroutine.
            maybe_coro = xmpp.disconnect()
            if asyncio.iscoroutine(maybe_coro):
                await asyncio.wait_for(maybe_coro, timeout=5)
        except Exception:  # noqa: BLE001 - shutdown must never raise
            pass
        try:
            await asyncio.wait_for(xmpp.disconnected, timeout=5)
        except Exception:  # noqa: BLE001
            pass
