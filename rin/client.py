from __future__ import annotations

import asyncio
import logging
import signal
from typing import TYPE_CHECKING, Any, Callable, TypeVar

import aiohttp
import attr

from .gateway import Collector, Dispatch, Event, Gateway, Listener
from .models import Intents, User
from .rest import RESTClient, Route
from .utils import ensure_loop

if TYPE_CHECKING:
    Callback = Callable[..., Any]
    Check = Callable[..., bool]

    T = TypeVar("T")

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

    token: str = attr.field(repr=False)
    intents: Intents = attr.field(kw_only=True, default=Intents.default())
    no_chunk: bool = attr.field(kw_only=True, default=False)
    loop: asyncio.AbstractEventLoop = attr.field(kw_only=True, default=None)

    rest: RESTClient = attr.field(init=False)
    gateway: Gateway = attr.field(init=False)
    dispatch: Dispatch = attr.field(init=False)
    closed: bool = attr.field(init=False, default=False)

    user: None | User = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.rest = RESTClient(self.token, self)
        self.dispatch = Dispatch(self)

    async def start(self, reconnect: bool = False) -> None:
        """Starts the connection.

        This method starts the connection to the gateway.
        """
        route = Route("gateway/bot")

        if reconnect is not True and self.loop is None:
            self.loop = ensure_loop()
            self.dispatch.loop = self.loop

        async def runner() -> None:
            if self.closed is True:
                return None

            data = await self.rest.request("GET", route)
            self.gateway = await self.rest.connect(data["url"])
            self.gateway._closed = False

            await self.gateway.start(self)

        def handle() -> None:
            self.loop.create_task(self.close("Received signal to terminate."))

        self.loop.add_signal_handler(signal.SIGTERM, handle)
        self.loop.add_signal_handler(signal.SIGINT, handle)

        await runner()

    async def close(self, reason: str = "None") -> None:
        """Closes the client.

        This method closes the gateway connection as
        well as the :class:`aiohttp.ClientSession` used by RESTClient.

        Parameters
        ----------
        reason: :class:`str`
            The reason to close the client with.
        """
        _log.debug("CLOSING CLIENT")
        session: aiohttp.ClientSession = self.rest.session
        self.closed = True

        await session.close()
        await self.gateway.close(reason=reason)

    def unserialize(self, data: dict[Any, Any], *, cls: type[T]) -> T:
        """Un-serializes a serialized object. Used for persistent objects.

        .. note::

            Objects could be inaccurate or outdated. It's suggested
            that you verify the object to be correct.

        Parameters
        ----------
        data: :class:`dict`
            The data of the object. This is retrieved via :meth:`.Base.serialize`.

        cls: :class:`type`
            The class to create via the data given.

        returns
        -------
        :class:`object`
            The object created with the data.
        """
        return cls(self, data)

    def collect(
        self, event: Event[Any], *, amount: int, check: Check = lambda *_: True
    ) -> Callable[..., Collector]:
        """Registers a collector to an event.

        Arguments of the callback will be passed as lists when
        the event has been collected X amount of times.

        Parameters
        ----------
        event: :class:`.Event`
            The event to register to.

        amount: :class:`int`
            The amount to collect before dispatching.

        check: Callable[..., bool]
            The check needed to be valid in order to collect
            an event.

        Returns
        -------
        Callable[..., :class:`.Collector`]
        """

        def inner(func: Callback) -> Collector:
            ret = event.subscribe(func, amount=amount, check=check)
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

        Returns
        -------
        Callable[..., :class:`.Listener`]
        """

        def inner(func: Callback) -> Listener:
            ret = event.subscribe(func, check=check)
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

        Returns
        -------
        Callable[..., :class:`.Listener`]
        """

        def inner(func: Callback) -> Listener:
            ret = event.subscribe(func, once=True, check=check)
            assert isinstance(ret, Listener)

            return ret

        return inner
