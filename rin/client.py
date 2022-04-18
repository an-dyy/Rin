from __future__ import annotations

import asyncio
from typing import Any, cast

import aiohttp
from attrs import define, field
from typing_extensions import Self

from .gateway import Gateway
from .interface import EventEmitter

__all__ = ["GatewayClient"]


@define(slots=True)
class GatewayClient:
    """A client used to communicate with discord.
    Interfaces both, the websocket and the REST API.

    Parameters
    ----------
    intents: :class:`int`
        The intents to use for the gateway,

    token: :class:`str`
        The token to use for authorisation.

    version: :class:`int`
        The version of the gateway to use.

    Attributes
    ----------
    intents: :class:`int`
        The intents to use for the gateway.

    token: :class:`str`
        The token to use for authorisation.

    version: :class:`int`
        The version of the gateway to use.

    loop: :class:`asyncio.AbstractEventLoop`
        The event loop to use.

    http_session: :class:`aiohttp.ClientSession`
        The session to use for HTTP requests.

    gateway: :class:`Gateway`
        The gateway client.

    emitter: :class:`EventEmitter`
        The event emitter.
    """

    intents: int = field()
    token: str = field(repr=False)
    version: int = field(default=9)

    loop: asyncio.AbstractEventLoop = field(init=False)
    http_session: aiohttp.ClientSession = field(init=False)

    gateway: Gateway = field(init=False)
    emitter: EventEmitter = field(init=False)

    async def connect(self) -> None:
        """Connects to the gateway & prepares the client."""
        self.http_session = aiohttp.ClientSession(ws_response_class=Gateway)

        self.gateway = cast(
            Gateway,
            await self.http_session.ws_connect(
                f"wss://gateway.discord.gg/?v={self.version}&encoding=json"
            ),
        )

        self.gateway.setup(self, self.intents, self.token)
        self.emitter = self.gateway.emitter

    async def close(self) -> None:
        """Closes the client."""
        await self.http_session.close()

    async def __aenter__(self) -> tuple[Self, Gateway]:
        await self.connect()
        return self, self.gateway

    async def __aexit__(self, *_: Any) -> None:
        await self.close()
