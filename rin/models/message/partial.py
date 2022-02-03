from __future__ import annotations

from typing import TYPE_CHECKING

import attr

from ...rest import Route
from ..builders import EmbedBuilder
from ..message import Message

if TYPE_CHECKING:
    from ...client import GatewayClient

__all__ = ("PartialSender",)


@attr.s(slots=True)
class PartialSender:
    client: GatewayClient = attr.field()
    snowflake: int = attr.field()

    async def send(
        self,
        content: None | str,
        *,
        tts: bool = False,
        embed: None | EmbedBuilder = None,
        embeds: list[EmbedBuilder] = [],
    ) -> Message:
        route = Route(f"channels/{self.snowflake}/messages", channel_id=self.snowflake)

        if embed is not None:
            embeds.append(embed)

        if len(embeds) > 10:
            raise ValueError("Cannot send a message with more than 10 embeds.")

        payload = {
            "content": content,
            "tts": tts,
            "embeds": [embed.to_dict() for embed in embeds],
        }
        data = await self.client.rest.request("POST", route, json=payload)

        return Message(self.client, data)
