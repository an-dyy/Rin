from __future__ import annotations

from typing import TYPE_CHECKING, Any

from datetime import datetime

import attr

from rin.models.message.types import MessageType

from ..base import BaseModel
from ..cacheable import Cacheable
from ..builders import EmbedBuilder
from ..snowflake import Snowflake
from ..user import User

if TYPE_CHECKING:
    from ...client import GatewayClient

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
        If the message was sent with text-to-speach.

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
    member: dict[Any, Any] = BaseModel.field(None, dict)

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

    @BaseModel.property("embeds", list[EmbedBuilder])
    def embeds(
        self, _: GatewayClient, data: list[dict[Any, Any]]
    ) -> list[EmbedBuilder]:
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

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        self.type = MessageType(self.data["type"])
        Message.cache.set(self.snowflake, self)
