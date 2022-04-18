from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Coroutine

from attrs import define, field
from loguru import logger

from .emitter import EventEmitter
from .events import Events

if TYPE_CHECKING:
    from ..client import GatewayClient

__all__ = ["PARSERS", "EventManager", "parses"]


PARSERS: dict[Events, Callable[..., Coroutine[Any, Any, Any]]] = {}


def parses(event: Events) -> Callable[..., Callable[..., Coroutine[Any, Any, Any]]]:
    """Marks a parser for the specified Event.

    Parameters
    ----------
    event: :class:`.Events`
        The event to mark the parser for.
    """

    def inner(
        func: Callable[..., Coroutine[Any, Any, Any]]
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        logger.info(f"PARSERS => {event} :: {func.__name__}")

        PARSERS[event] = func
        return func

    return inner


@define(slots=True)
class EventManager:
    """An Event manager.
    This class is used to "manage" events.
    This is done by parsing them, then emitting.

    Parameters
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The event loop to use.
    """

    client: GatewayClient = field()
    loop: asyncio.AbstractEventLoop = field()

    emitter: EventEmitter = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.emitter = EventEmitter(self.loop)

    async def parse(self, event: Events, data: dict[str, Any]) -> None:
        """Parses the event.

        Parameters
        ----------
        event: :class:`.Events`
            The event to parse.

        data: :class:`dict`
            The data to parse.
        """

        if parser := PARSERS.get(event):
            await parser(self, data)

    def emit(self, event: Events, *args: Any, **kwargs: Any) -> None:
        """Calls the emitter.

        Parameters
        ----------
        event: :class:`.Events`
            The event to emit.

        args: Any
            The arguments to pass to the event.

        kwargs: Any
            The keyword arguments to pass to the event.

        """
        self.emitter.emit(event, *args, **kwargs)

    @parses(Events.READY)
    async def ready(self, data: dict[str, Any]) -> None:
        self.emit(Events.READY, data)

    @parses(Events.GUILD_CREATE)
    async def guild_create(self, data: dict[str, Any]) -> None:
        self.emit(Events.GUILD_CREATE, data)

    @parses(Events.MESSAGE_CREATE)
    async def message_create(self, data: dict[str, Any]) -> None:
        self.emit(Events.MESSAGE_CREATE, data)
