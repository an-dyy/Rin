from __future__ import annotations

import attr

import aiohttp

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable

from .gateway import Collector, Dispatch, Event, Gateway, Listener
from .models import User
from .rest import RESTClient, Route

if TYPE_CHECKING:
    Callback = Callable[..., Any]
    Check = Callable[..., bool]

__all__ = ("GatewayClient",)
_log = logging.getLogger(__name__)


@attr.s(slots=True)
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

    token: str = attr.field()
    intents: int = attr.field(kw_only=True, default=1)
    loop: None | asyncio.AbstractEventLoop = attr.field(kw_only=True, default=None)

    rest: RESTClient = attr.field(init=False)
    gateway: Gateway = attr.field(init=False)
    dispatch: Dispatch = attr.field(init=False)
    closed: bool = attr.field(init=False, default=False)

    user: None | User = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        if self.loop is None:
            self.loop = asyncio.get_running_loop()

        self.rest = RESTClient(self.token, self)
        self.dispatch = Dispatch(self)

    async def start(self) -> None:
        """Starts the connection.

        This method starts the connection to the gateway.
        """
        route = Route("gateway/bot")

        if self.loop is None:
            self.loop = asyncio.get_running_loop()

        async def runner() -> None:
            data = await self.rest.request("GET", route)
            self.gateway = await self.rest.connect(data["url"])

            await self.gateway.start(self)

        while not self.closed:
            await runner()
            await asyncio.wait_for(self.gateway.reconnect_future, None)

    async def close(self) -> None:
        """Closes the client.

        This method closes the gateway connection as
        well as the :class:`aiohttp.ClientSession` used by RESTClient.
        """
        _log.debug("CLOSING CLIENT")
        self.closed = True

        session: aiohttp.ClientSession = self.rest.session
        await session.close()
        await self.gateway.close()

    def subscribe(
        self,
        event: Event,
        func: Callback,
        *,
        once: bool = False,
        collect: None | int = None,
        check: Check = lambda *_: True,
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
        self, event: Event, *, amount: int, check: Check = lambda *_: True
    ) -> Callback:
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

        def inner(func: Callback) -> Callback:
            self.subscribe(event, func, collect=amount, check=check)
            return func

        return inner

    def on(self, event: Event, check: Check = lambda *_: True) -> Callback:
        """Registers a callback to an event.

        Parameters
        ----------
        event: :class:`.Event`
            The event to register to.

        check: Callable[..., :class:`bool`]
            The check the event has to pass in order to be dispatched.
        """

        def inner(func: Callback) -> Callback:
            self.subscribe(event, func, check=check)
            return func

        return inner

    def once(self, event: Event, check: Check = lambda *_: True) -> Callback:
        """Registers a onetime callback to an event.

        Parameters
        ----------
        event: :class:`.Event`
            The event to register to.

        check: Callable[..., :class:`bool`]
            The check the event has to pass in order to be dispatched.
        """

        def inner(func: Callback) -> Callback:
            self.subscribe(event, func, once=True, check=check)
            return func

        return inner
