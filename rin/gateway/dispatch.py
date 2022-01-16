from __future__ import annotations

import collections
import logging
from typing import TYPE_CHECKING, Any, Callable
import asyncio

from ..models import User
from .event import Event

if TYPE_CHECKING:
    from ..client import GatewayClient

    Listeners = collections.defaultdict[
        str, list[tuple[Callable[..., Any], Callable[..., bool]]]
    ]

    Collectors = dict[
        str, tuple[asyncio.Queue[Any], Callable[..., Any], Callable[..., bool]]
    ]


__all__ = ("Dispatch",)
_log = logging.getLogger(__name__)


class Dispatch:
    def __init__(self, client: GatewayClient) -> None:
        self.loop = client.loop
        self.client = client

        self.listeners: Listeners = collections.defaultdict(list)
        self.once: Listeners = collections.defaultdict(list)
        self.collectors: Collectors = {}

    def __setitem__(
        self,
        event: tuple[str, bool],
        func: tuple[Callable[..., Any], Callable[..., bool]],
    ) -> None:
        _log.debug(
            f"DISPATCHER: Appending {func[0].__name__!r} to (event={Event(event[0].upper())}, once={event[1]})"
        )
        name, once = event

        if once is not False:
            self.once[name].append(func)

        elif once is False:
            self.listeners[name].append(func)

    def __call__(self, name: str, *payload: Any) -> None:
        _log.debug(f"DISPATCHING: {name.upper()}")
        name = name.lower()

        for once, check in self.once[name][:]:
            if check(*payload):
                self.loop.create_task(once(*payload))
                self.once[name].pop()

        for listener, check in self.listeners[name]:
            if check(*payload):
                self.loop.create_task(listener(*payload))

        if self.collectors.get(name):
            queue, callback, check = self.collectors[name]

            if check(*payload):
                self.loop.create_task(
                    self.dispatch_collector(queue, callback, *payload)
                )

        for wildcard, check in self.listeners["*"]:
            if check(*payload):
                self.loop.create_task(wildcard(name, *payload))

    async def dispatch_collector(
        self, queue, callback: Callable[..., Any], *data: Any
    ) -> None:
        await queue.put(data)
        queue.task_done()

        if queue.full():
            items = list(zip(*[queue.get_nowait() for _ in range(queue.maxsize)]))
            self.loop.create_task(callback(*items))

    async def no_parse(self, name: str, data: dict[Any, Any]) -> None:
        self(name, data)

    async def parse_ready(self, data: dict[Any, Any]) -> None:
        self("ready", User(self.client, data["user"]))
