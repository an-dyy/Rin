from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import attr

from ..base import BaseModel
from ..cacheable import Cacheable
from ..channels import TextChannel
from ..snowflake import Snowflake
from .emoji import Emoji
from .role import Role
from .types import MFALevel, VerificationLevel

if TYPE_CHECKING:
    from .member import Member
    from ...client import GatewayClient
    from ...typings import ChunkPayload


@attr.s(slots=True)
class Guild(BaseModel, Cacheable):
    """Represents a Guild object.

    Attributes
    ----------
    snowflake: :class:`.Snowflake`
        The snowflake of the Guild.

    name: :class:`str`
        The name of the guild.

    features: :class:`list`
        A list of enabled guild features. This is a list of :class:`str`.

    icon: None | :class:`str`
        The icon hash of the guild.

    icon_hash: None | :class:`str`
        The icon hash of the guild. Returned when in the template object

    splash: None | :class:`str`
        The hash of the guild's splash.

    discovery_splash: None | :class:`str`
        The hash of the discovery splash. Only given if the guild has enabled `DISCOVERABLE`.

    owner: :class:`bool`
        If the current authorized user is the owner of the guild.

    owner_id: :class:`.Snowflake`
        The snowflake of the guild's owner.

    permissions: None | :class:`str`
        The permissions of the current authorized user.

    region: None | :class:`str`
        The region of the guild.

    afk_channel_id: None | :class:`.Snowflake`
        The snowflake of the guild's AFK chanenl.

    afk_timeout: :class:`int`
        The amount of seconds before a user is considered AFK inside of the guild.

    widget_enabled: :class:`bool`
        If widgets are enabled.

    widget_channel_id: None | :class:`.Snowflake`
        The snowflake of the widget channel.

    mfa_level: :class:`.MFALevel`
        The MFA level of the guild.

    verification_level: :class:`.VerificationLevel`
        The verification level of the guild.

    system_channel_id: None | :class:`.Snowflake`
        The snowflake of the system channel inside of the guild.

    rules_channel_id: None | :class:`.Snowflake`
        The snowflake of the rules channel inside of the guild.

    large: :class:`bool`
        If this guild is considered "large".

    unavailable: :class:`bool`
        If this guild is unavailable

    member_count: :class:`int`
        The amount of members in the guild.
    """

    snowflake: Snowflake = BaseModel.field("id", Snowflake, repr=True)
    name: str = BaseModel.field(None, str, repr=True)
    features: list[str] = BaseModel.field(None, list[str])

    icon: None | str = BaseModel.field(None, str)
    icon_hash: None | str = BaseModel.field(None, str)
    splash: None | str = BaseModel.field(None, str)
    discover_splash: None | str = BaseModel.field(None, str)

    owner: bool = BaseModel.field(None, bool, default=False)
    owner_id: Snowflake = BaseModel.field(None, Snowflake)
    permissions: None | str = BaseModel.field(None, str)
    region: None | str = BaseModel.field(None, str)

    afk_channel_id: None | Snowflake = BaseModel.field(None, Snowflake)
    afk_timeout: int = BaseModel.field(None, int)

    widget_enabled: bool = BaseModel.field(None, bool, default=False)
    widget_channel_id: None | Snowflake = BaseModel.field(None, Snowflake)

    system_channel_id: None | Snowflake = BaseModel.field(None, Snowflake)
    rules_channel_id: None | Snowflake = BaseModel.field(None, Snowflake)

    large: bool = BaseModel.field(None, bool, repr=True)
    unavailable: bool = BaseModel.field(None, bool)
    member_count: int = BaseModel.field(None, int, default=0, repr=True)

    def __attrs_post_init__(self) -> None:
        self.members: list[Member] = []

        super().__attrs_post_init__()
        Guild.cache.set(self.snowflake, self)

    async def chunk(
        self,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: int | list[int] = [],
        nonce: None | str = None,
    ) -> None:
        payload: ChunkPayload = {
            "op": 8,
            "d": {
                "guild_id": self.snowflake,
                "query": query,
                "limit": limit,
                "presences": presences,
                "user_ids": user_ids,
                "nonce": nonce,
            },
        }

        await self.client.gateway.send(payload)

    @BaseModel.property("mfa_level", MFALevel)
    def mfa_level(self, _: GatewayClient, data: int) -> MFALevel:
        return MFALevel(data)

    @BaseModel.property("verification_level", VerificationLevel)
    def verification_level(self, _: GatewayClient, data: int) -> VerificationLevel:
        return VerificationLevel(data)

    @BaseModel.property("joined_at", datetime)
    def joined_at(self, _: GatewayClient, data: str) -> datetime:
        return datetime.fromisoformat(data)

    @BaseModel.property("roles", list[Role])
    def roles(self, client: GatewayClient, data: list[dict[str, Any]]) -> list[Role]:
        return [Role(client, r) for r in data]

    @BaseModel.property("emojis", list[Emoji])
    def emojis(self, client: GatewayClient, data: list[dict[str, Any]]) -> list[Emoji]:
        return [Emoji(client, e) for e in data]

    @BaseModel.property("channels", list[TextChannel])
    def text_channels(
        self, client: GatewayClient, data: list[dict[str, Any]]
    ) -> list[TextChannel]:
        return [TextChannel(client, t) for t in data]
