from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine, Generic, TypeVar

from attrs import define, field
from loguru import logger

from .events import Events

__all__ = ["Listener", "Collector", "EventEmitter"]

CallT = TypeVar("CallT", bound=Callable[..., Coroutine[Any, Any, Any]])


@define(slots=True)
class Listener(Generic[CallT]):
    """A listener.
    Basically a wrapper class for the callback.

    Attributes
    ----------
    callback: :class:`Callable`
        The callback to be called. Must be a coroutine.

    once: :class:`bool`
        Whether the listener should be removed after the first call.
    """

    once: bool = field()
    callback: CallT = field()

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.callback(*args, **kwargs)


@define(slots=True)
class Collector(Generic[CallT]):  # TODO: IMPL
    """A collector.
    Basically a wrapper class for the callback.
    Only dispatched once called X given times.

    Attributes
    ----------
    callback: :class:`Callable`
        The callback to be called. Must be a coroutine.

    once: :class:`bool`
        Whether the listener should be removed after the first call.
    """

    once: bool = field()
    callback: CallT = field()

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.callback(*args, **kwargs)


@define(slots=True)
class EventEmitter:
    """An Event emitter.
    Handles subscribing & emitting events.

    Attributes
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop to use.

    listeners: :class:`defaultdict`
        A dictionary of listeners.

    collectors: :class:`defaultdict`
        A dictionary of collectors.
    """

    loop: asyncio.AbstractEventLoop = field()
    listeners: dict[Events, list[Listener[Any]]] = field(init=False)
    collectors: dict[Events, list[Collector[Any]]] = field(init=False)

    def __attrs_post_init__(self):
        self.listeners = defaultdict(list)
        self.collectors = defaultdict(list)

    def subscribe(
        self, event: Events, callback: CallT, **kwargs: Any
    ) -> Listener[CallT] | Collector[CallT]:
        """Subscribes a callback to an event.

        Parameters
        ----------
        event: :class:`Events`
            The event to subscribe to.

        callback: :class:`Callable`
            The callback to be called. Must be a coroutine.

        once: :class:`bool`
            Whether the listener should be removed after the first call.

        collector: :class:`bool`
            If a collector should be registered.

        Raises
        ------
        :exc:`TypeError`
            If the callback is not a coroutine.

        Returns
        -------
        :class:`Listener` | :class:`Collector`
            The registered collector or listener.
        """

        logger.info(f"SUBSCRIBING {callback} => {event}")

        if not asyncio.iscoroutinefunction(callback):
            raise TypeError("Callback must be a coroutine function.") from None

        once = kwargs.get("once", False)
        if kwargs.get("collector", False):
            collector = Collector[CallT](once=once, callback=callback)
            self.collectors[event].append(collector)

            return collector

        listener = Listener[CallT](once=once, callback=callback)
        self.listeners[event].append(listener)

        return listener

    def emit(self, event: Events, *args: Any, **kwargs: Any) -> None:
        """Emit an event.

        Parameters
        ----------
        event: :class:`Events`
            The event to emit.

        args: :class:`Any`
            The arguments to pass to the listeners.

        kwargs: :class:`Any`
            The keyword arguments to pass to the listeners.
        """
        logger.info(f"EMITTING {event}")

        for index, listener in enumerate(self.listeners[event][:]):
            self.loop.create_task(listener(*args, **kwargs))

            if listener.once is True:
                self.listeners[event].pop(index)

        for idx, collector in enumerate(self.collectors[event][:]):
            self.loop.create_task(collector(*args, **kwargs))

            if collector.once is True:
                self.collectors[event].pop(idx)

    def on(self, event: Events) -> Callable[[CallT], Listener[CallT]]:
        """Registers a listener to the event.

        Parameters
        ----------
        event: :class:`Events`
            The event to subscribe to.
        """

        def inner(func: CallT) -> Listener[CallT]:
            subbed = self.subscribe(event, func, once=False)
            assert isinstance(subbed, Listener)  # IMPOSSBLE, HERE FOR TYPEHINTING

            return subbed

        return inner

    def once(self, event: Events) -> Callable[[CallT], Listener[CallT]]:
        """Registers a one-time listener to the event.

        Parameters
        ----------
        event: :class:`Events`
            The event to subscribe to.
        """

        def inner(func: CallT) -> Listener[CallT]:
            subbed = self.subscribe(event, func, once=True)
            assert isinstance(subbed, Listener)  # IMPOSSBLE, HERE FOR TYPEHINTING

            return subbed

        return inner

    def collect(self, event: Events) -> Callable[[CallT], Collector[CallT]]:
        """Registers a collector to the event.

        Parameters
        ----------
        event: :class:`Events`
            The event to subscribe to.
        """

        def inner(func: CallT) -> Collector[CallT]:
            subbed = self.subscribe(event, func, once=True, collector=True)
            assert isinstance(subbed, Collector)  # IMPOSSBLE, HERE FOR TYPEHINTING

            return subbed

        return inner
