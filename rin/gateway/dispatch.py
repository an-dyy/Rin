from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import attr

from .event import Event
from .parser import Parser

if TYPE_CHECKING:
    from ..client import GatewayClient

__all__ = ("Dispatch",)
_log = logging.getLogger(__name__)


@attr.s(slots=True)
class Dispatch:
    client: GatewayClient = attr.field()

    parser: Parser = attr.field(init=False)
    loop: asyncio.AbstractEventLoop = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.loop = self.client.loop
        self.parser = Parser(self.client, self)

    def __call__(self, event: Event[Any], *payload: Any) -> list[asyncio.Task[Any]]:
        _log.debug(f"DISPATCHER: DISPATCHING {event.name}")
        tasks: list[asyncio.Task[Any]] = []
        self.loop = self.client.loop

        for once in event.temp[:]:
            if once.check(*payload):
                tasks.append(self.loop.create_task(once(*payload)))
                event.temp.pop()

        for future, check in event.futures[:]:
            if check(*payload):
                future.set_result(*payload)
                event.futures.pop()

        for listener in event.listeners:
            if listener.check(*payload):
                tasks.append(self.loop.create_task(listener(*payload)))

        for collector in event.collectors:
            if not collector.check(*payload):
                return tasks

            tasks.append(self.loop.create_task(collector.dispatch(self.loop, *payload)))

        return tasks
