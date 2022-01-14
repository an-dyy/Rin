from __future__ import annotations

import collections
import logging
from typing import TYPE_CHECKING, Any, Callable

from ..models import User

if TYPE_CHECKING:
    from rin.types import UserData

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
        _log.debug(
            f"DISPATCHER: Appending {func.__name__!r} to (event={event[0]}, once={event[1]})"
        )
        name, once = event

        if once is not False:
            self.once[name].append(func)

        elif once is False:
            self.listeners[name].append(func)

    async def __call__(
        self, name: str, data: dict[Any, Any]
    ) -> None:  # TODO: Allow custom classes to events
        _log.debug(f"DISPATCHING: {name.upper()}")

        name = name.lower()
        parser = getattr(self, f"parse_{name}", self.no_parse)
        parsed = await parser(data)

        for once in self.once[name][:]:
            self.loop.create_task(once(parsed))
            self.once.popitem()

        for listener in self.listeners[name]:
            self.loop.create_task(listener(parsed))

        for wildcard in self.listeners["*"]:
            self.loop.create_task(wildcard(name, parsed))

    async def no_parse(self, data: dict[Any, Any]) -> dict[Any, Any]:
        return data

    async def parse_ready(self, data: dict[Any, Any]) -> User:
        return self.create_user(data["user"])

    def create_user(self, data: UserData) -> User:
        user = User(self.client, data)
        User.cache.set(user.id, user)

        return user
