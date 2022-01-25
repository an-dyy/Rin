from __future__ import annotations

import asyncio
import enum
import logging
import sys
from typing import TYPE_CHECKING, Any, Awaitable, Callable

import aiohttp

from .event import Events
from .ratelimiter import Ratelimiter

if TYPE_CHECKING:
    from rin.types import DispatchData, HeartbeatData, IdentifyData, ResumeData

    from ..client import GatewayClient

    PayloadData = IdentifyData | DispatchData | ResumeData | HeartbeatData

__all__ = ("Gateway",)

_log = logging.getLogger(__name__)


class OPCode(enum.IntFlag):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class Gateway(aiohttp.ClientWebSocketResponse):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._loop: asyncio.AbstractEventLoop
        self._closed: bool
        self._closed: bool

        self.ratelimiter = Ratelimiter(2, 1)
        self.client: GatewayClient
        self.intents: int

        self.interval: float = 0
        self.pacemaker: asyncio.Task[None]
        self.reconnect_future: asyncio.Future[None]

        self.session_id = ""
        self.sequence = 0

        self.close_reason: None | str = None

        self.callbacks: dict[int, Callable[..., Awaitable[Any]]] = {
            int(OPCode.DISPATCH): self.send_dispatch,
            int(OPCode.RESUME): self.send_resume,
            int(OPCode.RECONNECT): self.reconnect,
        }

    async def send_dispatch(self, data: dict[Any, Any]) -> None:
        dispatch = self.client.dispatch
        event = getattr(Events, data["t"])

        assert self.client.loop is not None
        if event == "READY":
            self.session_id = data["d"]["session_id"]

        parser = getattr(dispatch.parser, f"parse_{event.name.lower()}", None)

        if parser is not None:
            self._loop.create_task(parser(data["d"]))

        elif parser is None:
            self._loop.create_task(dispatch.parser.no_parse(event, data["d"]))

        for wildcard in Events.WILDCARD.listeners:
            if wildcard.check(event, data["d"]):
                self.client.loop.create_task(wildcard(event, data["d"]))

        for future, check in Events.WILDCARD.futures[:]:
            if check(event, data["d"]):
                future.set_result((event, data["d"]))
                Events.WILDCARD.futures.remove((future, check))

        for collector in Events.WILDCARD.collectors:
            if collector.check(event, data["d"]):
                self.client.loop.create_task(
                    collector.dispatch(self.client.loop, event, data["d"])
                )

    async def send_resume(self, _: dict[Any, Any]) -> None:
        return await self.send(self.resume)

    async def reconnect(self, _: dict[Any, Any]) -> None:
        _log.debug("GATEWAY SENT RECONNECT: CLOSING WEBSOCKET")
        if not self.closed:
            await self.close()

        self.reconnect_future.set_result(None)

    async def start(self, client: GatewayClient) -> None:
        _log.debug("CREATING GATEWAY FROM CLIENT.")
        assert client.loop is not None

        self.reconnect_future = client.loop.create_future()

        self.client = client
        self.intents = client.intents.value

        data = await self.receive_json()
        self.interval = data["d"]["heartbeat_interval"]
        self.pacemaker = self._loop.create_task(self.pulse())

        await self.send(self.identify)
        await self.read_messages()

    async def close(self, *args: Any, **kwargs: Any) -> Any:
        if self.pacemaker is not None and not self.pacemaker.cancelled():
            self.pacemaker.cancel()

        self.close_reason = kwargs.pop("reason", None)
        return await super().close(*args, **kwargs)

    async def send(self, payload: PayloadData) -> None:
        async with self.ratelimiter as _:
            await self.send_json(payload)

        _log.debug(f"SENT GATEWAY: {payload}")

    async def pulse(self) -> None:
        while self.interval is not None and not self._closed:
            await self.send(self.heartbeat)
            self.sequence += 1

            await asyncio.sleep(self.interval / 1000)

    async def read_messages(self) -> None:
        async for message in self:
            if message.type is aiohttp.WSMsgType.TEXT:  # type: ignore
                received = message.json()

                if sequence := received.get("s"):
                    self.sequence = sequence

                if callback := self.callbacks.get(received["op"]):
                    await callback(received)

                elif received["op"] == OPCode.HEARTBEAT_ACK:
                    _log.debug("GATEWAY ACK: HEARTBEAT")

        _log.debug(f"WEBSOCKET CLOSED WITH CODE: {self.close_code} REASON: {self.close_reason}")

    @property
    def identify(self) -> IdentifyData:
        return {
            "op": int(OPCode.IDENTIFY),
            "d": {
                "token": self.client.rest.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "Rin 0.1.0-alpha",
                    "$device": "Rin 0.1.0-alpha",
                },
            },
        }

    @property
    def resume(self) -> ResumeData:
        return {
            "op": int(OPCode.RESUME),
            "d": {
                "token": self.client.rest.token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        }

    @property
    def heartbeat(self) -> HeartbeatData:
        return {"op": int(OPCode.HEARTBEAT), "d": self.sequence}
