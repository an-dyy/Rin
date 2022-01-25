from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ..models import User
from .event import Event, Events

if TYPE_CHECKING:
    from ..client import GatewayClient
    from .dispatch import Dispatch


@attr.s(slots=True)
class Parser:
    client: GatewayClient = attr.field()
    dispatch: Dispatch = attr.field()

    async def no_parse(self, event: Event[Any], data: dict[Any, Any]) -> None:
        self.dispatch(event, data)

    async def parse_ready(self, data: dict[Any, Any]) -> None:
        user = User(self.client, data["user"])
        self.client.user = user

        self.dispatch(Events.READY, user)
