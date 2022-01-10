from __future__ import annotations

import asyncio
import inspect
import typing

from .gateway import Dispatcher, Gateway
from .rest import RESTClient, Route

__all__ = ("GatewayClient",)


class GatewayClient:
    __slots__ = ("rest", "intents", "gateway", "loop", "dispatcher")

    def __init__(self, token: str, *, loop: None | asyncio.AbstractEventLoop = None, intents: int = 1) -> None:
        self.loop = loop or self._create_loop()
        self.rest = RESTClient(token)
        self.intents = intents

        self.gateway: Gateway
        self.dispatcher = Dispatcher(self)

    def _create_loop(self) -> asyncio.AbstractEventLoop:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop

    def subscribe(self, name: str, func: typing.Callable[[typing.Any], typing.Any], *, once: bool = False) -> None:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Listener callback must be Coroutine.") from None

        self.dispatcher[(name, once)] = func

    def on(self, name: None | str = None) -> typing.Callable[[typing.Any], typing.Any]:
        def inner(func: typing.Callable[[typing.Any], typing.Any]) -> typing.Callable[[typing.Any], typing.Any]:
            self.subscribe(name or func.__name__, func)
            return func

        return inner

    def once(self, name: None | str = None) -> typing.Callable[[typing.Any], typing.Any]:
        def inner(func: typing.Callable[[typing.Any], typing.Any]) -> typing.Callable[[typing.Any], typing.Any]:
            self.subscribe(name or func.__name__, func, once=True)
            return func

        return inner

    async def start(self, *, show_payload: bool = False) -> None:
        data = await self.rest.request("GET", Route("gateway/bot"))
        self.gateway = await Gateway.from_url(self, data["url"], show_payload=show_payload)

        await self.gateway.read()
