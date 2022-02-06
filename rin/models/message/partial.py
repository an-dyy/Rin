from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ...rest import Route
from ..builders import EmbedBuilder
from .mentions import AllowedMentions

if TYPE_CHECKING:
    from ...client import GatewayClient
    from .components import ActionRowBuilder
    from .message import Message

__all__ = ("PartialSender",)


@attr.s(slots=True)
class PartialSender:
    client: GatewayClient = attr.field()
    snowflake: int = attr.field()

    async def send(
        self,
        content: None | str = None,
        tts: bool = False,
        embed: None | EmbedBuilder = None,
        embeds: list[EmbedBuilder] = [],
        reply: None | Message = None,
        allowed_mentions: None | AllowedMentions = None,
        rows: list[ActionRowBuilder] = [],
    ) -> Message:
        route = Route(f"channels/{self.snowflake}/messages", channel_id=self.snowflake)

        if embed is not None:
            embeds.append(embed)

        if len(embeds) > 10:
            raise ValueError("Cannot send a message with more than 10 embeds.")

        payload: dict[Any, Any] = {
            "content": content,
            "tts": tts,
            "embeds": [embed.to_dict() for embed in embeds],
            "components": [row.build() for row in rows],
        }

        print(payload["components"])

        if allowed_mentions is not None:
            payload["allowed_mentions"] = allowed_mentions.to_dict()

        if reply is not None:
            payload["message_reference"] = reply.to_reference()

        data = await self.client.rest.request("POST", route, json=payload)
        message: Message = self.client.gateway.parser.create_message(data)
        return message
