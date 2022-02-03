from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import attr

from ...rest import Route
from ..base import Base
from ..cacheable import Cacheable
from ..user import User

if TYPE_CHECKING:
    from .guild import Guild

__all__ = ("Member",)


@attr.s(slots=True)
class Member(Base, Cacheable):
    id: int = Base.field(cls=int, repr=True)
    guild: Guild = Base.field()

    user: User = Base.field(cls=User, has_client=True)
    roles: list[dict[Any, Any]] = Base.field()

    nick: None | str = Base.field()
    avatar: None | str = Base.field()

    deaf: bool = Base.field(repr=True)
    mute: bool = Base.field(repr=True)

    premium_since: datetime = Base.field(constructor=datetime.fromisoformat)
    joined_at: datetime = Base.field(constructor=datetime.fromisoformat)

    pending: bool = Base.field(default=False)
    permissions: str = Base.field()

    timeout: None | datetime = Base.field(
        key="communications_disabled_until", constructor=datetime.isoformat
    )

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        self.id = self.user.id
        self.username = self.user.username
        self.discriminator = self.user.discriminator

        Member.cache[self.id] = self

    def __str__(self) -> str:
        return f"{self.username}#{self.discriminator}"

    async def ban(self, delete_days: int = 0) -> None:
        """Bans a member from the guild.

        Parameters
        ----------
        delete_days: :class:`int`
            The amount of days of messages to delete from the user.

        Raises
        ------
        :exc:`.HTTPEXception`
            Something went wrong.
        """
        route = Route(f"guilds/{self.guild.id}/bans/{self.id}", guild_id=self.guild.id)

        await self.client.rest.request(
            "PUT", route, json={"delete_message_days": delete_days}
        )

    async def unban(self) -> None:
        """Unbans a member from the guild.

        Raises
        ------
        :exc:`.HTTPEXception`
            Something went wrong.
        """
        route = Route(f"guilds/{self.guild.id}/bans/{self.id}", guild_id=self.guild.id)
        await self.client.rest.request("DELETE", route)

    @property
    def mention(self) -> str:
        """The mention string to the user."""
        return f"<@{self.id}>"

    @property
    def bot(self) -> bool:
        """If the user is a bot."""
        return self.user.data.get("bot", False)

    @property
    def system(self) -> bool:
        """If the user is a system user."""
        return self.user.data.get("system", False)

    @property
    def mfa_enabled(self) -> bool:
        """If the user has 2fa enabled."""
        return self.user.data.get("mfa_enabled", False)

    @property
    def verified(self) -> bool:
        """If the user is verified or not."""
        return self.user.data.get("verified") or False
