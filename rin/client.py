from __future__ import annotations

import asyncio
import inspect
import typing

from .gateway import Dispatcher, Gateway
from .rest import RESTClient, Route

__all__ = ("GatewayClient",)


class GatewayClient:
    """A client which makes a connection to the gateway.

    This client is used to receive events from the gateway. This
    client also can utilize RESTful requests.

    Parameters
    ----------
    token: :class:`str`
        The token to use for authorization.

    loop: Optional[:class:`asyncio.AbstractEventLoop`]
        The loop to use for async operations.

    intents: :class:`int`
        The intents to identify with when connecting to the gateway.

    Attributes
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The loop being used for async operations.

    rest: :class:`.RESTClient`
        The RESTful request handler.

    intents: :class:`int`
        The intents the client is registered with.

    gateway: :class:`.Gateway`
        The gateway handler for the client.

    dispatcher: :class:`.Dispatcher`
        The dispatch manager for the client.

    """
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
        """Used to subscribe a callback to an event.

        Parameters
        ----------
        name: :class:`str`
            The name of the event to register to.

        func: Callable[Any, Any]
            The callback to register to the event.

        once: :class:`bool`
            If the callback should be ran once per lifetime.
        """
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Listener callback must be Coroutine.") from None

        self.dispatcher[(name, once)] = func

    def on(self, name: None | str = None) -> typing.Callable[[typing.Any], typing.Any]:
        """Registers a callback to an event.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the event to register to.
        """
        def inner(func: typing.Callable[[typing.Any], typing.Any]) -> typing.Callable[[typing.Any], typing.Any]:
            self.subscribe(name or func.__name__, func)
            return func

        return inner

    def once(self, name: None | str = None) -> typing.Callable[[typing.Any], typing.Any]:
        """Registers a onetime callback to an event.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the event to register to.
        """
        def inner(func: typing.Callable[[typing.Any], typing.Any]) -> typing.Callable[[typing.Any], typing.Any]:
            self.subscribe(name or func.__name__, func, once=True)
            return func

        return inner

    async def start(self, *, show_payload: bool = False) -> None:
        """Starts the connection.

        Parameters
        ----------
        show_payload: :class:`bool`
            If payloads should be shown in debug logs. This will
            only show if logging level is set to DEBUG.
        """
        data = await self.rest.request("GET", Route("gateway/bot"))
        self.gateway = await Gateway.from_url(self, data["url"], show_payload=show_payload)

        await self.gateway.read()
