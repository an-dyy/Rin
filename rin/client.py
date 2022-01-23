from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable

import aiohttp
import attr

from .gateway import Collector, Dispatch, Event, Gateway, Listener
from .models import User, Intents
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
    intents: Intents = attr.field(kw_only=True, default=Intents.default())
    loop: asyncio.AbstractEventLoop = attr.field(kw_only=True, default=None)  # type: ignore

    rest: RESTClient = attr.field(init=False)
    gateway: Gateway = attr.field(init=False)
    dispatch: Dispatch = attr.field(init=False)
    closed: bool = attr.field(init=False, default=False)

    user: None | User = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.rest = RESTClient(self.token, self)
        self.dispatch = Dispatch(self)

    async def start(self) -> None:
        """Starts the connection.

        This method starts the connection to the gateway.
        """
        route = Route("gateway/bot")

        if self.loop is None:
            self.loop = asyncio.get_running_loop()
            self.dispatch.loop = self.loop

        async def runner() -> None:
            if self.closed is True:
                return None

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
        self, event: Event[Any], func: Callback, **kwargs: Any
    ) -> Listener | Collector:
        """Subscribes a callback to an :class:`.Event`

        Parameters
        ----------
        event: :class:`.Event`
            The event to subscribe the callback to.

        func: Callable[..., Any]
            The callback being subscribed.

        once: :class:`bool`
            If this should be considered a one-time subscription.

        amount: :class:`int`
            How many times to collect the event before dispatching. This determines
            if the listener should be considered a :class:`.Collector`

        check: Callable[..., bool]
            A check the event has to pass in order to dispatch.

        Raises
        ------
        :exc:`TypeError`
            Raised when the callback is not a coroutine function.

        Returns
        -------
        :class:`.Listener` | :class:`.Collector`
            The created listener or collector.
        """
        check: Check = kwargs.get("check") or (lambda *_: True)

        if amount := kwargs.get("amount"):
            collector = Collector(func, check, asyncio.Queue[Any](maxsize=amount))
            event.collectors.append(collector)

            return collector

        listener = Listener(func, check)
        if kwargs.get("once", False) is not False:
            event.temp.append(listener)
            return listener

        event.listeners.append(listener)
        return listener

    def collect(
        self, event: Event[Any], *, amount: int, check: Check = lambda *_: True
    ) -> Callable[..., Collector]:
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

        def inner(func: Callback) -> Collector:
            ret = self.subscribe(event, func, amount=amount, check=check)
            assert isinstance(ret, Collector)

            return ret

        return inner

    def on(
        self, event: Event[Any], check: Check = lambda *_: True
    ) -> Callable[..., Listener]:
        """Registers a callback to an event.

        Parameters
        ----------
        event: :class:`.Event`
            The event to register to.

        check: Callable[..., :class:`bool`]
            The check the event has to pass in order to be dispatched.
        """

        def inner(func: Callback) -> Listener:
            ret = self.subscribe(event, func, check=check)
            assert isinstance(ret, Listener)

            return ret

        return inner

    def once(
        self, event: Event[Any], check: Check = lambda *_: True
    ) -> Callable[..., Listener]:
        """Registers a onetime callback to an event.

        Parameters
        ----------
        event: :class:`.Event`
            The event to register to.

        check: Callable[..., :class:`bool`]
            The check the event has to pass in order to be dispatched.
        """

        def inner(func: Callback) -> Listener:
            ret = self.subscribe(event, func, once=True, check=check)
            assert isinstance(ret, Listener)

            return ret

        return inner
