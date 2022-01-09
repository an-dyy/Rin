from __future__ import annotations

import asyncio

from .gateway import Gateway
from .rest import RESTClient

__all__ = ("GatewayClient",)


class GatewayClient:
    __slots__ = ("rest", "intents", "gateway", "loop")

    def __init__(self, token: str, *, loop: None | asyncio.AbstractEventLoop = None, intents: int = 1) -> None:
        self.loop = loop or self._create_loop()
        self.rest = RESTClient(token)
        self.intents = intents

        self.gateway: Gateway

    def _create_loop(self) -> asyncio.AbstractEventLoop:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            return loop

    async def start(self) -> None:
        gateway = await Gateway.from_url(self, "url")
        await gateway.read()

        self.gateway = gateway
