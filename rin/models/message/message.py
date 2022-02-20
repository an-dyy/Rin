from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import attr

from ...rest import Route
from ..assets import File
from ..base import BaseModel
from ..builders import EmbedBuilder
from ..cacheable import Cacheable
from ..snowflake import Snowflake
from ..user import User
from ..guild import Member
from .mentions import AllowedMentions
from .types import MessageType

if TYPE_CHECKING:
    from ...client import GatewayClient
    from .components import ActionRow

__all__ = ("Message",)


@attr.s(slots=True)
class Message(BaseModel, Cacheable, max=1000):
    """Represents a Message.

    Attributes
    ----------
    snowflake: :class:`.Snowflake`
        The snowflake of the message.

    channel_id: :class:`.Snowflake`
        The snowflake of the message's parent channel.

    guild_id: None | :class:`.Snowflake`
        The snowflake of the guild the message was sent in. None
        if the message was sent inside of a direct-message channel.

    webhook_id: None | :class:`Snowflake`
        The snowflake of the webhook if the message was sent from one.

    application_id: None | :class:`.Snowflake`
        The snowflake of the message's application.

    user: :class:`.User`
        The user object of the user who sent the message.

    member: :class:`dict`
        The member object of the user who sent the message.

    content: :class:`str`
        The content of the message.

    tts: :class:`bool`
        If the message was sent with text-to-speech.

    mentioned_everyone: :class:`bool`
        If the message mentioned everyone.

    mention_roles: list[:class:`dict`]
        A list of mentioned roles in the message.

    mention_channels: list[:class:`dict`]
        A list of mentioned channels in the message.

    attachments: list[:class:`dict`]
        A list of attachments sent with the message.

    thread: None | :class:`dict`
        The thread the message was sent in, if any.

    sticker_items: list[:class:`dict`]
        A list of stickers sent with the message.

    reactions: list[:class:`dict`]
        A list of the reactions on the message.

    interaction: None | :class:`dict`
        The interaction of the message. Only given when the message is an interaction response.

    components: list[:class:`dict`]
        A list of message components sent with the message.

    nonce: None | :class:`str`
        Used for validating a message was sent.

    pinned: :class:`bool`
        If the message is pinned.

    type: :class:`.MessageType`
        The message's type.

    application: None | :class:`dict`
        The application of the message.

    message_reference: None | :class:`dict`
        The message's reference.

    embeds: list[:class:`.EmbedBuilder`]
        A list of embeds sent with the message.

    mentions: list[:class:`.User`]
        A list of mentioned users in the message.

    timestamp: :class:`datetime.datetime`
        The timestamp for when the message was created.

    editted_at: :class:`datetime.datetime`
        The time when the message was editted. None if the message hasn't
        been editted.
    """

    snowflake: Snowflake = BaseModel.field("id", Snowflake)
    channel_id: Snowflake = BaseModel.field(None, Snowflake)

    guild_id: None | Snowflake = BaseModel.field(None, Snowflake)
    webhook_id: None | Snowflake = BaseModel.field(None, Snowflake)
    application_id: None | Snowflake = BaseModel.field(None, Snowflake)

    user: User = BaseModel.field("author", User)
    member: Member = BaseModel.field(None, Member)

    content: str = BaseModel.field(None, str)
    tts: bool = BaseModel.field(None, bool)
    mentioned_everyone: bool = BaseModel.field("mention_everyone", bool)

    #  TODO: IMPLEMENT ALL THESE MODELS AND REPLACE TYPEHINT
    mention_roles: list[dict[Any, Any]] = BaseModel.field(None, list[dict[str, Any]])
    mention_channels: list[dict[Any, Any]] = BaseModel.field(None, list[dict[str, Any]])
    attachments: list[dict[Any, Any]] = BaseModel.field(None, list[dict[str, Any]])
    thread: None | dict[str, Any] = BaseModel.field(None, dict[str, Any])

    sticker_items: list[dict[str, Any]] = BaseModel.field(None, list[dict[str, Any]])
    reactions: list[dict[Any, Any]] = BaseModel.field(None, list[dict[str, Any]])

    interaction: None | dict[str, Any] = BaseModel.field(None, dict[str, Any])
    components: list[dict[str, Any]] = BaseModel.field(None, list[dict[str, Any]])

    nonce: None | str = BaseModel.field(None, str)
    pinned: bool = BaseModel.field(None, bool)

    application: None | dict[Any, Any] = BaseModel.field(None, dict[str, Any])
    message_reference: None | Message = BaseModel.field(None, dict[str, Any])

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        self.type = MessageType(self.data["type"])
        Message.cache.set(self.snowflake, self)

    @BaseModel.property("embeds", list[EmbedBuilder])
    def embeds(self, _: GatewayClient, data: list[dict[Any, Any]]) -> list[EmbedBuilder]:
        return [EmbedBuilder.from_dict(e) for e in data]

    @BaseModel.property("mentions", list[User])
    def mentions(self, client: GatewayClient, data: list[dict[Any, Any]]) -> list[User]:
        return [User.cache.get(user["id"]) or User(client, user) for user in data]

    @BaseModel.property("timestamp", datetime)
    def timestamp(self, _: GatewayClient, timestamp: str) -> datetime:
        return datetime.fromisoformat(timestamp)

    @BaseModel.property("editted_at", datetime)
    def editted_at(self, _: GatewayClient, timestamp: str) -> None | datetime:
        if timestamp is not None:
            return datetime.fromisoformat(timestamp)

    def reference(self) -> dict[str, Snowflake]:
        """Creates a message reference from the instance.

        Returns
        -------
        :class:`dict`
            The created dict representing the message's reference.
        """
        return {"message_id": self.snowflake}

    async def reply(
        self,
        content: None | str = None,
        tts: bool = False,
        embeds: list[EmbedBuilder] = [],
        files: list[File] = [],
        rows: list[ActionRow] = [],
        mentions: AllowedMentions = AllowedMentions(),
    ) -> Message:
        """Sends a message repyling to this message
        into the channel corresponding to the passed in :class:`.Snowflake`.

        Parameters
        ----------
        content: None | :class:`str`
            The content to give the message.

        tts: :class:`bool`
            If the message should be sent with text-to-speech. Defaults to False.

        embeds: :class:`list`
            A list of :class:`.EmbedBuilder` instances to send with the message.

        files: :class:`list`
            A list of :class:`.File` instances to send with the message.

        mentions: :class:`.AllowedMentions`
            The allowed mentions of the message.

        Returns
        -------
        :class:`.Message`
            An instance of the newly sent message.
        """
        sender = self.client.sender(self.channel_id)
        return await sender.send(content, tts, embeds, files, rows, self, mentions)

    async def delete(self) -> None:
        """Deletes the message.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong.
        """
        route = Route(
            f"/channels/{self.channel_id}/messages/{self.snowflake}",
            channel_id=self.channel_id,
        )

        Message.cache.pop(self.snowflake)
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
            f"channels/{self.channel_id}/messages/{self.snowflake}/reactions/{reaction}/@me",
            channel_id=self.channel_id,
        )

        await self.client.rest.request("PUT", route)

    async def delete_reaction(
        self, reaction: str, user: None | User | Snowflake | int = None
    ) -> None:
        """Deletes a reaction from the message.

        Parameters
        ----------
        reaction: :class:`str`
            The reaction to delete from the message.

        user: None | :class:`.User` | :class:`.Snowflake` | :class:`int`
            The user to remove the reaction from.
            If no user is passed the user will be defaulted to the current authorised user.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong.
        """
        path = "@me" if user is None else user
        if isinstance(path, User):
            path = path.snowflake

        route = Route(
            f"/channels/{self.channel_id}/messages/{self.snowflake}/reactions/{reaction}/{path}"
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
            f"channels/{self.channel_id}/pins/{self.snowflake}",
            channel_id=self.channel_id,
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
            f"channels/{self.channel_id}/pins/{self.snowflake}",
            channel_id=self.channel_id,
        )

        await self.client.rest.request("DELETE", route)
