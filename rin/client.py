from __future__ import annotations

import asyncio
import signal
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Callable, TypeVar

import aiohttp
import attr

from .gateway import Collector, Event, Gateway, Listener
from .models import IntentsBuilder, MessageBuilder, Snowflake
from .rest import RESTClient
from .utils import ensure_loop

if TYPE_CHECKING:
    from .models import User

    Callback = Callable[..., Any]
    Check = Callable[..., bool]

    T = TypeVar("T")

__all__ = ("GatewayClient",)


@attr.s(slots=True)
class GatewayClient:
    """A client which makes a connection to the gateway.

    This client is used to receive events from the gateway. This
    client also can utilize RESTful requests.

    Parameters
    ----------
    token: :class:`str`
        The token to use for authorization.

    no_chunk: :class:`bool`
        If chunking at startup should be disabled.

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
    intents: IntentsBuilder = attr.field(kw_only=True, default=IntentsBuilder.default())
    no_chunk: bool = attr.field(kw_only=True, default=False, repr=True)
    loop: asyncio.AbstractEventLoop = attr.field(kw_only=True, default=None, repr=False)

    rest: RESTClient = attr.field(init=False, repr=False)
    gateway: Gateway = attr.field(init=False, repr=False)
    closed: bool = attr.field(init=False, default=False, repr=True)

    user: None | User = attr.field(init=False, default=None, repr=False)

    def __attrs_post_init__(self) -> None:
        self.rest = RESTClient(self.token, self)
        self.gateway = Gateway(self)

    async def start(self) -> None:
        """Starts the connection.

        This method starts the connection to the gateway.
        """
        if self.loop is None:
            self.loop = ensure_loop()
            self.gateway.loop = self.loop

        async def runner() -> None:
            if self.closed is True:
                return None

            await self.gateway.start()

        def handle() -> None:
            self.loop.create_task(self.close())

        self.loop.add_signal_handler(signal.SIGTERM, handle)
        self.loop.add_signal_handler(signal.SIGINT, handle)

        await runner()

    async def close(self) -> None:
        """Closes the client.

        This method closes the gateway connection as
        well as the :class:`aiohttp.ClientSession` used by RESTClient.

        Parameters
        ----------
        reason: :class:`str`
            The reason to close the client with.
        """
        self.closed = True
        session: aiohttp.ClientSession = self.rest.session

        await session.close()
        await self.gateway.close()

    def sender(self, snowflake: Snowflake | int) -> MessageBuilder:
        """Creates a :class:`.MessageBuilder` from the client.

        Parameters
        ----------
        snowflake: :class:`.Snowflake` | :class:`int`
            The snowflake of the channel to create the builder for.

        Returns
        -------
        :class:`.MessageBuilder`
            The created MessageBuilder instance.
        """
        return MessageBuilder(self, snowflake)

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

    def dispatch(self, event: Event[Any], *payload: Any) -> list[asyncio.Task[Any]]:
        """Dispatches an event.

        Examples
        --------
        .. code:: python

            client.dispatch(rin.Events.MESSAGE_CREATE, rin.Message(...))
            # Here `rin.Message(...)` is the payload that gets dispatched to the event's callback.

        Parameters
        ----------
        event: :class:`.Event`
            The event to dispatch.

        payload: Any
            The payload to dispatch the event with.

        Returns
        -------
        list[:class:`asyncio.Task`]
            A list of tasks created by the dispatch call.
        """
        return event.dispatch(*payload, client=self)

    def collect(
        self,
        event: Event[Any],
        *,
        amount: int,
        timeout: None | timedelta = None,
        check: Check = lambda *_: True,
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
            ret = event.subscribe(func, amount=amount, check=check, timeout=timeout)
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
