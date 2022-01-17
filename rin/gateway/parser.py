from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import User
from .event import Event

if TYPE_CHECKING:
    from ..client import GatewayClient
    from .dispatch import Dispatch


class Parser:
    def __init__(self, client: GatewayClient, dispatch: Dispatch) -> None:
        self.dispatch = dispatch
        self.client = client

    async def no_parse(self, event: Event, data: dict[Any, Any]) -> None:
        self.dispatch(event, data)

    async def parse_ready(self, data: dict[Any, Any]) -> None:
        user = User(self.client, data["user"])
        self.client.user = user

        self.dispatch(Event.READY, user)
