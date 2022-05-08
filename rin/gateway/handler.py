from __future__ import annotations

import asyncio
import enum
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, cast

import aiohttp
import attr

from ..rest import Route
from .event import Events
from .parser import Parser
from .ratelimiter import Ratelimiter

if TYPE_CHECKING:
    from ..client import GatewayClient
    from ..models import IntentsBuilder
    from ..typings import (
        DispatchPayload,
        HeartbeatPayload,
        IdentifyPayload,
        ResumePayload,
    )

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


class WSMessage(NamedTuple):
    type: aiohttp.WSMsgType
    json: Callable[..., dict[Any, Any]]


@attr.s(slots=True)
class Gateway:
    client: GatewayClient = attr.field(repr=False)
    intents: IntentsBuilder = attr.field(init=False, repr=False)
    loop: asyncio.AbstractEventLoop = attr.field(init=False, repr=False)

    parser: Parser = attr.field(init=False, repr=False)
    ratelimiter: Ratelimiter = attr.field(
        init=False, default=Ratelimiter(2, 1), repr=False
    )

    interval: float = attr.field(init=False, default=0, repr=False)
    pacemaker: asyncio.Task[None] = attr.field(init=False, repr=False)
    last_heartbeat: None | datetime = attr.field(init=False, default=None)
    latency: float = attr.field(init=False, default=float("inf"))

    session: str = attr.field(init=False, default="", repr=True)
    sequence: int = attr.field(init=False, default=0, repr=True)

    sock: aiohttp.ClientWebSocketResponse = attr.field(init=False, repr=False)
    callbacks: dict[OPCode, Callable[..., Any]] = attr.field(init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        self.parser = Parser(self.client)
        self.intents = self.client.intents
        self.loop = self.client.loop

        self.callbacks = {
            OPCode.DISPATCH: self.dispatch,
            OPCode.RESUME: self.send_resume,
            OPCode.RECONNECT: self.send_reconnect,
        }

    async def __call__(self, payload: DispatchPayload) -> None:
        await self.send(payload)

    async def start(self) -> None:
        _log.debug("STARTING GATEWAY CONNECTION.")

        data = await self.client.rest.request("GET", Route("gateway/bot"))
        max_concurrency: int = data["session_start_limit"]["max_concurrency"]

        async with Ratelimiter(max_concurrency, 1):
            self.sock = await self.client.rest.connect(data["url"])

            data = await self.sock.receive_json()
            self.interval = data["d"]["heartbeat_interval"]
            self.pacemaker = self.loop.create_task(self.pulse())

            await self(self.identify)
            await self.read()

    async def close(self) -> None:
        _log.debug("CLOSING GATEWAY CONNECTION.")

        if not self.sock.closed:
            await self.sock.close()

    async def read(self) -> None:
        async for message in self.sock:
            message = cast(WSMessage, message)

            if message.type is not aiohttp.WSMsgType.TEXT:
                continue

            data = message.json()
            code = data["op"]

            if sequence := data.get("s"):
                self.sequence = sequence

            if callback := self.callbacks.get(OPCode(code)):
                await callback(data)

            if code == OPCode.HEARTBEAT_ACK:
                if self.last_heartbeat is not None:
                    self.latency = (datetime.now() - self.last_heartbeat).total_seconds()

                _log.debug("GATEWAY ACK'D HEARTBEAT.")

    async def dispatch(self, data: dict[Any, Any]) -> asyncio.Task[Any]:
        event = getattr(Events, data["t"])
        _log.debug(f"DISPATCHING {event}")

        if event is Events.READY:
            self.session = data["d"]["session_id"]

        parser = getattr(self.parser, f"parse_{event.name.lower()}", None)
        self.client.dispatch(Events.WILDCARD, event, data["d"])

        if parser is not None:
            return self.loop.create_task(parser(data["d"]))

        return self.loop.create_task(self.parser.no_parse(event, data["d"]))

    async def send_resume(self, _: dict[Any, Any]) -> None:
        _log.debug("GATEWAY SENT RESUME.")
        await self(self.resume)

    async def send_reconnect(self, _: dict[Any, Any]) -> None:
        _log.debug("GATEWAY SENT RECONNECT.")
        if not self.sock.closed:
            await self.sock.close()

        await self.start()

    async def send(self, payload: DispatchPayload) -> None:
        async with self.ratelimiter:
            _log.debug(f"SENDING GATEWAY: {payload}")

            await self.sock.send_json(payload)

    async def pulse(self) -> None:
        while not self.sock.closed:
            self.last_heartbeat = datetime.now()

            await self(self.heartbeat)
            self.sequence += 1

            await asyncio.sleep(self.interval / 1000)

    @property
    def identify(self) -> IdentifyPayload:
        return {
            "op": 2,
            "d": {
                "token": self.client.token,
                "intents": self.intents.value,
                "properties": {
                    "$os": "",
                    "$browser": "Rin 0.1.2-alpha",
                    "$device": "Rin 0.1.2-alpha",
                },
            },
        }

    @property
    def resume(self) -> ResumePayload:
        return {
            "op": 6,
            "d": {
                "token": self.client.token,
                "session_id": self.session,
                "seq": self.sequence,
            },
        }

    @property
    def heartbeat(self) -> HeartbeatPayload:
        return {"op": 1, "d": self.sequence}
