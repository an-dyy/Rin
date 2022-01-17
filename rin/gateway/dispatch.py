from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Awaitable, Callable, NamedTuple

from .event import Event
from .parser import Parser

if TYPE_CHECKING:
    from ..client import GatewayClient

__all__ = ("Dispatch", "Listener", "Collector")
_log = logging.getLogger(__name__)


class Listener(NamedTuple):
    callback: Callable[..., Awaitable[Any]]
    check: Callable[..., bool]


class Collector(NamedTuple):
    callback: Callable[..., Awaitable[Any]]
    check: Callable[..., bool]
    queue: asyncio.Queue[Any]

    async def dispatch(
        self, loop: asyncio.AbstractEventLoop, *payload: Any
    ) -> None | asyncio.Task[Any]:
        task: None | asyncio.Task[Any] = None

        await self.queue.put(payload)
        self.queue.task_done()

        if self.queue.full():
            items = [self.queue.get_nowait() for _ in range(self.queue.maxsize)]
            task = loop.create_task(self.callback(*list(zip(*items))))

        return task


class Dispatch:
    __slots__ = ("loop", "client", "parser", "listeners", "once", "collectors")

    def __init__(self, client: GatewayClient) -> None:
        self.parser: Parser = Parser(client, self)
        self.loop = client.loop
        self.client = client

        self.listeners: dict[Event, list[Listener]] = defaultdict(list)
        self.once: dict[Event, list[Listener]] = defaultdict(list)
        self.collectors: dict[Event, Collector] = {}

    def __call__(self, event: Event, *payload: Any) -> list[asyncio.Task[Any]]:
        _log.debug(f"DISPATCHER: DISPATCHING {event}")
        tasks: list[asyncio.Task[Any]] = []
        loop = self.loop

        for once in self.once[event][:]:
            if once.check(*payload):
                tasks.append(loop.create_task(once.callback(*payload)))
                self.once[event].pop()

        for listener in self.listeners[event]:
            if listener.check(*payload):
                tasks.append(loop.create_task(listener.callback(*payload)))

        if collector := self.collectors.get(event):
            if not collector.check(*payload):
                return tasks

            tasks.append(loop.create_task(collector.dispatch(*payload)))

        return tasks
