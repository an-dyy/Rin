from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable

from .gateway import Dispatch, Gateway, Event
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

    __slots__ = ("loop", "rest", "intents", "gateway", "dispatch")

    def __init__(
        self,
        token: str,
        *,
        loop: None | asyncio.AbstractEventLoop = None,
        intents: int = 1
    ) -> None:
        self.loop = loop or self._create_loop()
        self.rest = RESTClient(token, self)
        self.intents = intents

        self.gateway: Gateway
        self.dispatch = Dispatch(self)

    def _create_loop(self) -> asyncio.AbstractEventLoop:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop

    def subscribe(
        self, event: Event, func: Callable[..., Any], *, once: bool = False
    ) -> None:
        """Used to subscribe a callback to an event.

        Parameters
        ----------
        name: :class:`.Event`
            The the event to register to.

        func: Callable[..., Any]
            The callback to register to the event.

        once: :class:`bool`
            If the callback should be ran once per lifetime.

        Raises
        ------
        :exc:`TypeError`
            Raised when the callback is not a Coroutine.
        """
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Listener callback must be Coroutine.") from None

        self.dispatch[(event.value.lower(), once)] = func

    def on(self, event: Event) -> Callable[..., Any]:
        """Registers a callback to an event.

        Parameters
        ----------
        name: :class:`.Event`
            The event to register to.
        """

        def inner(func: Callable[..., Any]) -> Callable[..., Any]:
            self.subscribe(event, func)
            return func

        return inner

    def once(self, event: Event) -> Callable[..., Any]:
        """Registers a onetime callback to an event.

        Parameters
        ----------
        name: :class:`.Event`
            The event to register to.
        """

        def inner(func: Callable[..., Any]) -> Callable[..., Any]:
            self.subscribe(event, func, once=True)
            return func

        return inner

    async def start(self) -> None:
        """Starts the connection.

        This method creates the internal gateway handler and
        starts the pacemaker to keep the connect "alive". This also
        waits for reconnect dispatches to restart the gateway.
        """
        while True:
            data = await self.rest.request("GET", Route("gateway/bot"))
            self.gateway = await self.rest.connect(data["url"])

            await self.gateway.start(self)
            await asyncio.wait_for(self.gateway.reconnect_future, timeout=None)
