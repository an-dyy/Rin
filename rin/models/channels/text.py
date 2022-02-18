from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import attr

from ..base import BaseModel
from ..cacheable import Cacheable
from ..snowflake import Snowflake
from .types import ChannelType

if TYPE_CHECKING:
    from ...client import GatewayClient

__all__ = ("TextChannel",)


@attr.s(slots=True)
class TextChannel(BaseModel, Cacheable):
    """Represents a TextChannel object.

    Attributes
    ----------
    snowflake: :class:`.Snowflake`
        The channel's snowflake.

    type: :class:`.ChannelType`
        The type of the channel.

    name: :class:`str`
        The name of the channel.

    topic: None | :class:`str`
        The topic of the channel.

    nsfw: :class:`bool`
        If the TextChannel is marked as NSFW.

    guild_id: None | :class:`.Snowflake`
        The ID of the guild where the channel is. None if in a DM Channel.

    position: :class:`int`
        The position of the TextChannel in the guild.

    last_message_id: None | :class:`.Snowflake`
        The ID of the last sent message in the TextChannel.

    parent_id: None | :class:`.Snowflake`
        The ID of the TextChannel's parent channel, this being a Category channel.

    slowmode: :class:`int`
        The slowmode of the TextChannel.

    last_pin: None | :class:`datetime.datetime`
        The last known time at when a message was pinned in the channel.
    """

    snowflake: Snowflake = BaseModel.field(None, Snowflake, repr=True)

    name: str = BaseModel.field(None, str, repr=True)
    topic: None | str = BaseModel.field(None, str)
    nsfw: bool = BaseModel.field(None, bool, repr=True)

    guild_id: None | Snowflake = BaseModel.field(None, Snowflake)
    position: int = BaseModel.field(None, int)

    last_message_id: None | Snowflake = BaseModel.field(None, Snowflake)
    parent_id: None | Snowflake = BaseModel.field(None, Snowflake)

    slowmode: int = BaseModel.field("rate_limit_per_user", int, default=0)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        TextChannel.cache.set(self.snowflake, self)

    @BaseModel.property("type", ChannelType, repr=True)
    def type(self, _: GatewayClient, data: int) -> ChannelType:
        return ChannelType(data)

    @BaseModel.property("last_pinned_at", datetime)
    def last_pin(self, _: GatewayClient, data: None | str) -> None | datetime:
        if data is not None:
            return datetime.fromisoformat(data)
