from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from .gateway import Collector, Dispatch, Event, Gateway, Listener
from .models import User
from .rest import RESTClient, Route

__all__ = ("GatewayClient",)
_log = logging.getLogger(__name__)


class GatewayClient:
    """A client which makes a connection to the gateway.

    This client is used to receive events from the gateway. This
    client also can utilize RESTful requests.

    Parameters
    ----------
    token: :class:`str`
        The token to use for authorization.

    loop: None | :class:`asyncio.AbstractEventLoop`
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

    __slots__ = ("loop", "rest", "intents", "gateway", "dispatch", "user")

    def __init__(
        self,
        token: str,
        *,
        loop: None | asyncio.AbstractEventLoop = None,
        intents: int = 1,
    ) -> None:
        self.loop = loop or self._create_loop()
        self.rest = RESTClient(token, self)
        self.intents = intents

        self.gateway: Gateway
        self.dispatch = Dispatch(self)
        self.user: None | User = None

    def _create_loop(self) -> asyncio.AbstractEventLoop:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop

    def subscribe(
        self,
        event: Event,
        func: Callable[..., Any],
        *,
        once: bool = False,
        collect: None | int = None,
        check: Callable[..., bool] = lambda *_: True,
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

        collect: None | :class:`int`
            How many times to collect the event before dispatching
            all at once. Arguments for the callback will be passed as lists.

        check: Callable[..., :class:`bool`]
            The check the event has to pass in order to be dispatched.

        Raises
        ------
        :exc:`TypeError`
            Raised when the callback is not a Coroutine.
        """
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Listener callback must be Coroutine.") from None

        data = Listener(func, check)
        fmt = f"(Event={event}, amount={collect})"
        message = "DISPATCHER: Append {0} {1} {2}"
        name = func.__name__

        if collect is not None:
            self.dispatch.collectors[event] = Collector(
                func, check, asyncio.Queue[Any](maxsize=collect)
            )

            return _log.debug(message.format("Collector", name, fmt))

        elif once is not False:
            self.dispatch.once[event].append(data)
            return _log.debug(message.format("one-time", name, fmt))

        self.dispatch.listeners[event].append(data)
        return _log.debug(message.format("Listener", name, fmt))

    def collect(
        self, event: Event, *, amount: int, check: Callable[..., bool] = lambda *_: True
    ) -> Callable[..., Any]:
        """Registers a collector to an event.

        Arguments of the callback will be passed as lists when
        the event has been collected X amount of times.

        Parameters
        ----------
        name: :class:`.Event`
            The event to register to.

        amount: :class:`int`
            The amount to collect before dispatching.

        check: Callable[..., bool]
            The check needed to be valid in order to collect
            an event.
        """

        def inner(func: Callable[..., Any]) -> Callable[..., Any]:
            self.subscribe(event, func, collect=amount, check=check)
            return func

        return inner

    def on(
        self, event: Event, check: Callable[..., bool] = lambda *_: True
    ) -> Callable[..., Any]:
        """Registers a callback to an event.

        Parameters
        ----------
        event: :class:`.Event`
            The event to register to.

        check: Callable[..., :class:`bool`]
            The check the event has to pass in order to be dispatched.
        """

        def inner(func: Callable[..., Any]) -> Callable[..., Any]:
            self.subscribe(event, func, check=check)
            return func

        return inner

    def once(
        self, event: Event, check: Callable[..., bool] = lambda *_: True
    ) -> Callable[..., Any]:
        """Registers a onetime callback to an event.

        Parameters
        ----------
        event: :class:`.Event`
            The event to register to.

        check: Callable[..., :class:`bool`]
            The check the event has to pass in order to be dispatched.
        """

        def inner(func: Callable[..., Any]) -> Callable[..., Any]:
            self.subscribe(event, func, once=True, check=check)
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
