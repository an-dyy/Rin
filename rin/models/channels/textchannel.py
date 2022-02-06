from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import attr

from ..base import Base
from ..cacheable import Cacheable
from .types import ChannelType

if TYPE_CHECKING:
    from ..builders import EmbedBuilder
    from ..guild import Guild
    from ..message import ActionRowBuilder, AllowedMentions, Message

__all__ = ("TextChannel",)


@attr.s(slots=True)
class TextChannel(Base, Cacheable):
    id: int = Base.field(cls=int, repr=True)
    type: ChannelType = Base.field(default=ChannelType.GUILD_TEXT)

    guild_id: int = Base.field(cls=int, repr=True)
    guild: Guild = Base.field()

    name: str = Base.field(repr=True)
    topic: None | str = Base.field()
    nsfw: bool = Base.field(default=False, repr=True)
    position: int = Base.field(cls=int, repr=True)

    last_message_id: None | int = Base.field(cls=int)
    last_pinned_at: None | datetime = Base.field(
        key="last_pin_timestamp", constructor=datetime.fromisoformat
    )

    owner_id: None | int = Base.field(cls=int)
    parent_id: None | int = Base.field(cls=int)

    slowmode: int = Base.field(cls=int, default=0)
    overwrites: list[dict[Any, Any]] = Base.field(key="permission_overwrite")
    permissions: str = Base.field()

    async def send(
        self,
        content: None | str = None,
        tts: bool = False,
        embed: None | EmbedBuilder = None,
        embeds: list[EmbedBuilder] = [],
        allowed_mentions: None | AllowedMentions = None,
        rows: list[ActionRowBuilder] = [],
    ) -> Message:
        """Send a message in the channel.

        Parameters
        ----------
        content: None | str
            The content of the reply.

        tts: bool
            If text-to-speech should be used when replying.

        embed: None | :class:`EmbedBuilder`
            The embed to send with the reply.

        embeds: :class:`list`
            A list of embeds to send with the reply. Can only send 10 embeds at a time.

        allowed_mentions: None | :class:`.AllowedMentions`
            The allowed mentions of the reply.

        rows: :class:`list`
            A list of :class:`.ActionRow`s to use when sending.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong.

        Returns
        -------
        :class:`.Message`
            The newly created reply as a :class:`.Message` instance.
        """

        partial = self.client.gateway.parser.partial_sender(self.id)
        return await partial.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            rows=rows,
        )
