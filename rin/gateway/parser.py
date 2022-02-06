from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ..models import (
    ComponentCache,
    ComponentType,
    Guild,
    Interaction,
    InteractionType,
    Member,
    Message,
    TextChannel,
    User,
)
from .event import Event, Events

if TYPE_CHECKING:
    from ..client import GatewayClient


@attr.s(slots=True)
class Parser:
    client: GatewayClient = attr.field()

    async def no_parse(self, event: Event[Any], data: dict[Any, Any]) -> None:
        self.client.dispatch(event, data)

    async def parse_interaction_create(self, data: dict[Any, Any]) -> None:
        interaction = Interaction(self.client, data)

        if interaction.type is InteractionType.COMPONENT:
            if component := ComponentCache.cache.get(data["data"]["custom_id"]):

                if component.type is ComponentType.SELECTMENU:
                    component.values = interaction.data["data"]["values"]

                await component.callback(interaction, component)

        self.client.dispatch(Events.INTERACTION_CREATE, interaction)

    async def parse_ready(self, data: dict[Any, Any]) -> None:
        user = User(self.client, data["user"])
        self.client.user = user

        self.client.dispatch(Events.READY, user)

    async def parse_guild_create(self, data: dict[Any, Any]) -> None:
        guild = Guild(self.client, data)
        intents = self.client.intents

        if intents.guild_members is True and intents.guild_presences is False:
            if self.client.no_chunk is not True:
                await guild.chunk()

        self.client.dispatch(Events.GUILD_CREATE, guild)

    async def parse_guild_members_chunk(self, data: dict[Any, Any]) -> None:
        members = [Member(self.client, member_data) for member_data in data["members"]]
        if guild := Guild.cache.get(int(data["guild_id"])):
            guild.members = members

            for member in members:
                member.guild = guild

        self.client.dispatch(Events.GUILD_MEMBERS_CHUNK, members)

    async def parse_message_create(self, data: dict[Any, Any]) -> None:
        self.client.dispatch(Events.MESSAGE_CREATE, Message(self.client, data))

    async def parse_message_delete(self, data: dict[Any, Any]) -> None:
        message = Message.cache.root.pop(data["id"], data)
        self.client.dispatch(Events.MESSAGE_DELETE, message)

    async def parse_message_update(self, data: dict[Any, Any]) -> None:
        if TextChannel.cache.get(int(data["channel_id"])):
            before = Message.cache.get(int(data["id"]))
            after = Message(self.client, data)

            self.client.dispatch(Events.MESSAGE_UPDATE, before, after)

    def create_message(self, data: dict[Any, Any]) -> Message:
        return Message(self.client, data)
