from __future__ import annotations

import collections
import logging
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from ..client import GatewayClient

    Listeners = collections.defaultdict[str, list[Callable[..., Any]]]

_log = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, client: GatewayClient) -> None:
        self.loop = client.loop
        self.client = client

        self.listeners: Listeners = collections.defaultdict(list)
        self.once: Listeners = collections.defaultdict(list)

    def __setitem__(self, event: tuple[str, bool], func: Callable[..., Any]) -> None:
        _log.debug(f"DISPATCHER: Appending {func.__name__!r} to {event}")
        name, once = event

        if once is not False:
            self.once[name].append(func)

        elif once is False:
            self.listeners[name].append(func)

    def __call__(self, name: str, data: dict[Any, Any]) -> None:
        _log.debug(f"DISPATCHING: {name.upper()}")

        name = name.lower()
        parsed = data

        for once in self.once[name]:
            self.loop.create_task(once(parsed))
            return None

        for listener in self.listeners[name]:
            self.loop.create_task(listener(parsed))

        for wildcard in self.listeners["*"]:
            self.loop.create_task(wildcard(name, parsed))