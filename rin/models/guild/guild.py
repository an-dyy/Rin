from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

import attr

from ...rest import Route
from ...types import ChunkData
from ..base import Base
from ..cacheable import Cacheable
from ..channels import TextChannel
from ..snowflake import Snowflake
from .member import Member

if TYPE_CHECKING:
    Check = Callable[..., bool]

text_check: Check = lambda c: c["type"] == 0


@attr.s(slots=True)
class Guild(Base, Cacheable):
    id: int = Base.field(cls=int, repr=True)
    name: str = Base.field(repr=True)
    vanity: None | str = Base.field(key="vanity_url_code")
    premium_enabled: bool = Base.field(key="premium_progress_bar_enabled")

    description: None | str = Base.field()
    banner: None | str = Base.field()

    premium_tier: int = Base.field(cls=int)
    premium_subscription_count: None | int = Base.field(cls=int)
    preferred_locale: str = Base.field()

    icon: str = Base.field()
    icon_hash: None | str = Base.field()

    splash: None | str = Base.field()
    splash_has: None | str = Base.field()

    afk_channel_id: None | str = Base.field(cls=int)
    afk_timeout: int = Base.field(cls=int, default=0)

    widget_enabled: bool = Base.field(default=False)
    widget_channel_id: None | int = Base.field(cls=int)

    verification_level: int = Base.field(cls=int)
    default_message_notifications: int = Base.field(cls=int)
    explicit_content_filter: int = Base.field(cls=int)
    mfa_level: int = Base.field(cls=int)
    nsfw_level: int = Base.field(cls=int)

    application_id: None | int = Base.field(cls=int)
    public_updates_channel_id: None | int = Base.field(cls=int)
    rules_channel_id: None | int = Base.field(cls=int)
    system_channel_id: None | int = Base.field(cls=int)
    system_channel_flags: int = Base.field(cls=int)

    roles: list[dict[Any, Any]] = Base.field()
    emojis: list[dict[Any, Any]] = Base.field()
    stickers: list[dict[Any, Any]] = Base.field()

    features: list[dict[Any, Any]] = Base.field()
    welcome_screen: dict[Any, Any] = Base.field()
    guild_scheduled_events: list[dict[Any, Any]] = Base.field()

    members: list[Member] = Base.field(cls=Member, has_client=True)
    threads: list[dict[Any, Any]] = Base.field()
    presences: list[dict[Any, Any]] = Base.field()
    voice_states: list[dict[Any, Any]] = Base.field()
    stages: list[dict[Any, Any]] = Base.field(key="stage_instances")

    max_presences: None | int = Base.field(cls=int)
    max_members: None | int = Base.field(cls=int)
    member_count: None | int = Base.field(cls=int)

    approximate_member_count: None | int = Base.field(cls=int)
    approximate_presence_count: None | int = Base.field(cls=int)

    text_channels: list[TextChannel] = Base.field(
        cls=TextChannel, check=text_check, has_client=True, key="channels"
    )

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        for channel in self.text_channels:
            channel.guild = self

        for member in self.members:
            Member.cache.set(member.id, member)
            member.guild = self

    async def ban(self, user: Snowflake, delete_days: int = 0) -> None:
        """Bans a member from the guild.

        Parameters
        ----------
        user: :class:`.Snowflake`
            The user to ban from the guild.

        delete_days: :class:`int`
            The amount of days of messages to delete from the user.

        Raises
        ------
        :exc:`.HTTPEXception`
            Something went wrong.
        """
        route = Route(f"guilds/{self.id}/bans/{user.id}", guild_id=self.id)

        await self.client.rest.request(
            "PUT", route, json={"delete_message_days": delete_days}
        )

    async def unban(self, user: Snowflake) -> None:
        """Unbans a member from the guild.

        Parameters
        ----------
        user: :class:`.Snowflake`
            The user to unban from the guild.

        Raises
        ------
        :exc:`.HTTPEXception`
            Something went wrong.
        """
        route = Route(f"guilds/{self.id}/bans/{user.id}", guild_id=self.id)
        await self.client.rest.request("DELETE", route)

    async def chunk(
        self,
        query: str = "",
        limit: int = 0,
        presences: bool = False,
        user_ids: None | int | list[int] = None,
        nonce: None | str = None,
    ) -> None:
        payload: ChunkData = {
            "op": 8,
            "d": {
                "guild_id": self.id,
                "query": query,
                "limit": limit,
                "presences": presences,
                "user_ids": user_ids,
                "nonce": nonce,
            },
        }

        await self.client.gateway.send(payload)
