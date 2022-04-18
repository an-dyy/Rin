from __future__ import annotations

import asyncio
import random
import sys
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, cast

from aiohttp import ClientWebSocketResponse, WSMsgType
from loguru import logger

from ..interface import EventEmitter, EventManager, Events

if TYPE_CHECKING:
    from ..client import GatewayClient

__all__ = ["Gateway"]


class WSMessage(NamedTuple):
    json: Callable[..., dict[str, Any]]
    type: WSMsgType


class Gateway(ClientWebSocketResponse):
    """The gateway client.

    Attributes
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop to use.

    manager: :class:`EventManager`
        The event manager to use.

    emitter: :class:`EventEmitter`
        The event emitter to use.

    intents: :class:`int`
        The intents to use.

    token: :class:`str`
        The token to use.

    interval: :class:`float`
        The interval for the heartbeat.

    sequence: :class:`int`
        The sequence of events.

    session_id: :class:`str`
        The session id.
    """

    __slots__ = (
        "loop",
        "manager",
        "emitter",
        "intents",
        "token",
        "interval",
        "sequence",
        "session_id",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.loop: asyncio.AbstractEventLoop
        self.manager: EventManager
        self.emitter: EventEmitter

        self.intents: int
        self.token: str

        self.interval: float = 0
        self.sequence: int = 0
        self.session_id: str = ""

    @property
    def jitter(self) -> float:
        """The jitter for the heartbeat."""
        return random.random() * self.interval

    def setup(self, client: GatewayClient, intents: int, token: str) -> None:
        """Setup the gateway client.

        Parameters
        ----------
        client: :class:`GatewayClient`
            The client to use.

        intents: :class:`int`
            The intents to use.

        token: :class:`str`
            The token to use.
        """
        logger.info("SETTING UP WEBSOCKET ATTRIBUTES")

        self.loop = asyncio.get_running_loop()
        self.manager = EventManager(client, self.loop)
        self.emitter = self.manager.emitter

        self.intents = intents
        self.token = token
        self.client = client

    async def start(self) -> None:
        """Start the gateway client."""
        logger.info("STARTING WEBSOCKET")

        startup = await self.receive_json()
        self.interval = startup["d"]["heartbeat_interval"] / 1000

        self.start_ping()
        await self.send_identity()
        await self.reader()

    async def reader(self) -> None:
        """The reader for the gateway client."""
        logger.info("STARTED WEBSOCKET READER")

        async for message in self:
            message = cast(WSMessage, message)
            if message.type is not WSMsgType.TEXT:
                continue

            inbound = message.json()

            if sequence := inbound.get("s"):
                self.sequence = sequence

            if inbound.get("op") == 11:
                logger.info("HEARTBEAT ACK'D")
                continue

            await self.dispatch(inbound)

    async def dispatch(self, data: dict[str, Any]) -> None:
        """Dispatch the data to the event manager.

        Parameters
        ----------
        data: :class:`dict`
            The data to dispatch.
        """

        event = getattr(Events, data["t"], Events.UNKNOWN)
        code = data.get("op")

        if event is Events.READY:
            self.session_id = data["d"]["session_id"]

        if code == 1:
            await self.send_ping()

        elif code == 6:
            await self.send_resume()

        elif code == 7:
            await self.close()  # TODO: RECONNECTION IMPL

        await self.manager.parse(event, data)

    def start_ping(self) -> None:
        """Start the heartbeat."""

        async def loop() -> None:
            if not self.closed:
                await self.send_ping()
                logger.info("SENT HEARTBEAT")

            self.loop.call_later(self.jitter, self.start_ping)

        self.loop.create_task(loop())

    async def send_ping(self) -> None:
        """Send a heartbeat."""
        await self.send_json({"op": 1, "d": self.sequence})

    async def send_identity(self) -> None:
        """Send the identity."""
        logger.info("SENDING IDENTITY")

        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "Rin 0.1.0-alpha",
                    "$device": "Rin 0.1.0-alpha",
                },
            },
        }

        await self.send_json(payload)

    async def send_resume(self) -> None:
        """Send the resume."""
        logger.info("SENDING RESUME")

        payload = {
            "op": 6,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        }

        await self.send_json(payload)
