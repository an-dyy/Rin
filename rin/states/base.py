from __future__ import annotations

from typing import Coroutine, Callable, Any

import asyncio

from collections import defaultdict

CbT = Callable[..., Coroutine[Any, Any, None]]


class BaseState:
    """A base class for states,

    Attributes
    ----------
    listeners: :class:`dict`
        A dictionary of listeners.
    """

    def __init__(self) -> None:
        self.listeners: dict[str, list[CbT]] = defaultdict(list)

    def subscribe(self, callback: CbT, /, event: str) -> CbT:
        """Subbscribes to an event.

        Parameters
        ----------
        callback: :class:`Callable`
            The callback to be called when the event is emitted.

        event: :class:`str`
            The event to subscribe to.

        Raises
        ------
        :exc:`TypeError`
            If the callback is not a coroutine.

        Returns
        -------
        :class:`Callable`
            The callback.
        """

        if not asyncio.iscoroutinefunction(callback):
            raise TypeError(
                f"Callback {callback.__name__} must be a coroutine."
            ) from None

        self.listeners[event].append(callback)
        return callback

    def on(self, event: str) -> Callable[[CbT], CbT]:
        """Decorator for subscribing to an event.

        Parameters
        ----------
        event: :class:`str`
            The event to subscribe to.

        Returns
        -------
        :class:`Callable`
            The decorated function.
        """

        def inner(func: CbT) -> CbT:
            return self.subscribe(func, event)

        return inner

    async def emit(self, event: str, payload: dict[str, Any]) -> None:
        """Emits an event with the given payload.

        Parameters
        ----------
        event: :class:`str`
            The event to emit.

        payload: :class:`dict`
            The payload to emit.
        """
        loop = asyncio.get_running_loop()

        for listener in self.listeners[event]:
            loop.create_task(listener(*(await self.parse(payload))))

    async def parse(self, payload: dict[str, Any]) -> tuple[Any, ...]:
        """Parses the payload emitted.
        This is called to determine what to pass to listeners.

        Parameters
        ----------
        payload: :class:`dict`
            The payload to parse.

        Returns
        -------
        :class:`tuple`
            The parsed payload.
        """
        raise NotImplementedError
