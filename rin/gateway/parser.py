from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ..models import Guild, Message, TextChannel, User
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

    async def parse_guild_create(self, data: dict[Any, Any]) -> None:
        self.dispatch(Events.GUILD_CREATE, Guild(self.client, data))

    async def parse_message_create(self, data: dict[Any, Any]) -> None:
        self.dispatch(Events.MESSAGE_CREATE, Message(self.client, data))

    async def parse_message_delete(self, data: dict[Any, Any]) -> None:
        message = Message.cache.root.pop(data["id"], data)
        self.dispatch(Events.MESSAGE_DELETE, message)

    async def parse_message_update(self, data: dict[Any, Any]) -> None:
        if TextChannel.cache.get(int(data["channel_id"])):
            before = Message.cache.get(int(data["id"]))
            after = Message(self.client, data)

            self.dispatch(Events.MESSAGE_UPDATE, before, after)
