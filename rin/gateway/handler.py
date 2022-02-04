from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, cast

import aiohttp
import attr

from ..rest import Route
from .event import Events
from .parser import Parser
from .payloads import HEARTBEAT, IDENTIFY, RESUME, OPCode, format
from .ratelimiter import Ratelimiter

if TYPE_CHECKING:
    from ..client import GatewayClient
    from ..models import Intents
    from ..types import PayloadData

__all__ = ("Gateway",)
_log = logging.getLogger(__name__)


class WSMessage(NamedTuple):
    type: aiohttp.WSMsgType
    json: Callable[..., dict[Any, Any]]


@attr.s(slots=True)
class Gateway:
    client: GatewayClient = attr.field(repr=False)
    intents: Intents = attr.field(init=False, repr=False)
    loop: asyncio.AbstractEventLoop = attr.field(init=False, repr=False)

    parser: Parser = attr.field(init=False, repr=False)
    ratelimiter: Ratelimiter = attr.field(
        init=False, default=Ratelimiter(2, 1), repr=False
    )

    interval: float = attr.field(init=False, default=0, repr=False)
    pacemaker: asyncio.Task[None] = attr.field(init=False, repr=False)

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
            OPCode.RESUME: self.resume,
            OPCode.RECONNECT: self.reconnect,
        }

    async def __call__(self, payload: PayloadData) -> None:
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

            await self(format(IDENTIFY, self.client.token, self.intents.value))
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

    async def resume(self, _: dict[Any, Any]) -> None:
        _log.debug("GATEWAY SENT RESUME.")
        await self(format(RESUME, self.client.token, self.sequence))

    async def reconnect(self, _: dict[Any, Any]) -> None:
        _log.debug("GATEWAY SENT RECONNECT.")
        if not self.sock.closed:
            await self.sock.close()

        await self.start()

    async def send(self, payload: PayloadData) -> None:
        async with self.ratelimiter:
            _log.debug(f"SENDING GATEWAY: {payload}")

            await self.sock.send_json(payload)

    async def pulse(self) -> None:
        while not self.sock.closed:

            await self(format(HEARTBEAT, self.sequence))
            self.sequence += 1

            await asyncio.sleep(self.interval / 1000)
