from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import attr

from ...rest import Route
from ..base import Base
from ..cacheable import Cacheable
from ..channels import TextChannel
from ..snowflake import Snowflake
from ..user import User
from .partial import PartialSender

if TYPE_CHECKING:
    from ..builders import EmbedBuilder
    from ..guild import Guild
    from .mentions import AllowedMentions

__all__ = ("Message",)


@attr.s(slots=True)
class Message(Base, Cacheable, max=1000):
    id: int = Base.field(cls=int, repr=True)
    channel: TextChannel = Base.field()

    channel_id: int = Base.field(cls=int, repr=True)
    guild_id: int = Base.field(cls=int)
    guild: Guild = Base.field()

    user: User = Base.field(cls=User)
    member: dict[Any, Any] = Base.field()
    author: User | dict[Any, Any] = Base.field()

    content: str = Base.field()
    timestamp: datetime = Base.field(constructor=datetime.fromisoformat)
    editted_timestamp: datetime = Base.field(constructor=datetime.fromisoformat)

    tts: bool = Base.field()
    mentioned_everyone = Base.field(key="mention_everyone")

    mentions: list[User] = Base.field(cls=User, has_client=True)
    mentioned_roles: list[dict[Any, Any]] = Base.field()
    mentioned_channels: list[dict[Any, Any]] = Base.field()

    referenced: None | dict[Any, Any] = Base.field(key="referenced_message")

    thread: None | dict[Any, Any] = Base.field()
    attachments: list[dict[Any, Any]] = Base.field()
    embeds: list[dict[Any, Any]] = Base.field()
    reactions: list[dict[Any, Any]] = Base.field()
    activity: dict[Any, Any] = Base.field()

    nonce: None | str = Base.field()
    pinned: bool = Base.field()

    webhook_id: None | int = Base.field(cls=int)
    application_id: None | int = Base.field(cls=int)
    application: None | dict[Any, Any] = Base.field()

    type: int = Base.field(cls=int)
    flags: None | int = Base.field(cls=int)

    interaction: None | dict[Any, Any] = Base.field()
    components: None | list[dict[Any, Any]] = Base.field()

    stickers: None | list[dict[Any, Any]] = Base.field(key="sticker_items")

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        self.channel = TextChannel.cache[self.channel_id]
        self.author = self.member or self.user

    def to_reference(self) -> dict[str, int]:
        """Creates a reference dict from the message.

        This is used for replies.

        Returns
        -------
        :class:`dict`
            The created dict for the message.
        """
        payload = {"message_id": self.id, "channel_id": self.channel.id}

        if self.guild:
            payload["guild_id"] = self.guild.id

        return payload

    async def reply(
        self,
        content: None | str = None,
        tts: bool = False,
        embed: None | EmbedBuilder = None,
        embeds: list[EmbedBuilder] = [],
        allowed_mentions: None | AllowedMentions = None,
    ) -> Message:
        """Replies to the message.

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

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong.

        Returns
        -------
        :class:`.Message`
            The newly created reply as a :class:`.Message` instance.
        """

        partial = PartialSender(self.client, self.channel.id)
        return await partial.send(
            reply=self,
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
        )

    async def delete(self) -> None:
        """Deletes the message.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong.
        """
        route = Route(
            f"/channels/{self.channel_id}/messages/{self.id}",
            channel_id=self.channel_id,
        )

        Message.cache.pop(self.id)
        await self.client.rest.request("DELETE", route)

    async def react(self, reaction: str) -> None:
        """Adds a reaction to the message.

        Parameters
        ----------
        reaction: :class:`str`
            The reaction to react with.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong.
        """
        route = Route(
            f"channels/{self.channel_id}/messages/{self.id}/reactions/{reaction}/@me",
            channel_id=self.channel_id,
        )

        await self.client.rest.request("PUT", route)

    async def delete_reaction(
        self, reaction: str, user: None | Snowflake = None
    ) -> None:
        """Deletes a reaction from the message.

        Parameters
        ----------
        reaction: :class:`str`
            The reaction to delete from the message.

        user: None | :class:`.Snowflake`
            The user to remove the reaction from. If no user is passed
            the user will be defaulted to the current authorised user.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong.
        """
        path = "@me" if user is None else user.id
        route = Route(
            f"/channels/{self.channel_id}/messages/{self.id}/reactions/{reaction}/{path}"
        )

        await self.client.rest.request("DELETE", route)

    async def pin(self) -> None:
        """Pins the message.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong while making the request.
        """
        route = Route(
            f"channels/{self.channel_id}/pins/{self.id}", channel_id=self.channel_id
        )

        await self.client.rest.request("PUT", route)

    async def unpin(self) -> None:
        """Unpins the message.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong while making the request.
        """
        route = Route(
            f"channels/{self.channel_id}/pins/{self.id}", channel_id=self.channel_id
        )

        await self.client.rest.request("DELETE", route)
