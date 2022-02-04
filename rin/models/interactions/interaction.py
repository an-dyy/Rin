from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ...rest import Route
from ..base import Base
from ..builders import EmbedBuilder
from ..channels import TextChannel
from ..guild import Member
from ..message.mentions import AllowedMentions
from ..message.message import Message
from ..user import User
from .types import InteractionResponse, InteractionType

if TYPE_CHECKING:
    from ...client import GatewayClient

__all__ = ("Interaction",)


@attr.s(slots=True)
class Interaction(Base):
    client: GatewayClient = Base.field(init=True)
    data: dict[Any, Any] = Base.field(key=None, cls=None, init=True)

    id: int = Base.field(cls=int)
    application_id: int = Base.field(cls=int)

    guild_id: None | int = Base.field(cls=int)
    channel_id: None | int = Base.field(cls=int)

    type = Base.field(cls=InteractionType)
    message: None | Message = Base.field(cls=Message, has_client=True)
    raw: dict[Any, Any] = Base.field(key=None)

    member: None | Member = Base.field(cls=Member, has_client=True)
    user: None | User = Base.field(cls=User, has_client=True)

    locale: None | str = Base.field()
    guild_locale: None | str = Base.field()

    token: str = Base.field()
    version: str = Base.field()

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        self.raw = self.data["data"]

    @property
    def channel(self) -> None | TextChannel:
        if self.channel_id is not None and self.message is not None:
            return TextChannel.cache.get(self.channel_id)

    @property
    def author(self) -> None | User | Member:
        return self.member or self.user

    async def send(
        self,
        content: None | str = None,
        tts: bool = False,
        embed: None | EmbedBuilder = None,
        embeds: list[EmbedBuilder] = [],
        reply: None | Message = None,
        allowed_mentions: None | AllowedMentions = None,
        ephemeral: bool = False,
    ) -> Message:
        route = Route(f"interactions/{self.id}/{self.token}/callback")

        if embed is not None:
            embeds.append(embed)

        if len(embeds) > 10:
            raise ValueError("Cannot send a message with more than 10 embeds.")

        payload: dict[Any, Any] = {
            "content": content,
            "tts": tts,
            "embeds": [embed.to_dict() for embed in embeds],
        }

        if allowed_mentions is not None:
            payload["allowed_mentions"] = allowed_mentions.to_dict()

        if reply is not None:
            payload["message_reference"] = reply.to_reference()

        if ephemeral is not False:
            payload["flags"] = 64

        data: dict[str, InteractionResponse | dict[Any, Any]] = {
            "type": InteractionResponse.MESSAGE,
            "data": payload,
        }

        await self.client.rest.request("POST", route, json=data)
        ret = await self.client.rest.request(
            "GET",
            Route(f"/webhooks/{self.application_id}/{self.token}/messages/@original"),
        )

        return Message(self.client, ret)
