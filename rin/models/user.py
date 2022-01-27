from __future__ import annotations

import attr

from .base import Base
from .cacheable import Cacheable

__all__ = ("User",)


@attr.s(slots=True)
class User(Base, Cacheable):
    """Represents a User.

    .. note::
        |cacheable|

    Attributes
    ----------
    id: :class:`int`
        The ID of the user.

    username: :class:`str`
        The username of the user.

    discriminator: :class:`str`
        The discriminator of the user.

    avatar: None | :class:`str`
        The avatar of the user.

    banner: None | :class:`str`
        The banner of the user.

    color: :class:`int`
        The accent color of the user.

    locale: None | :class:`str`
        The locale of the user, E.g `en_US`

    email: None | :class:`str`
        The email of the user.

    flags: :class:`int`
        The flags of the user.

    public_flags: :class:`int`
        The public flags of the user.

    premium: :class:`int`
        The premium type of the user.
    """

    id: int = Base.field(key="id", cls=int)

    username: str = Base.field(key="username")
    discriminator: str = Base.field(key="discriminator")

    avatar: None | str = Base.field(key="avatar")
    banner: None | str = Base.field(key="banner")
    color: None | int = Base.field(key="color", cls=int)

    locale: None | str = Base.field(key="locale")
    email: None | str = Base.field(key="locale")

    flags: int = Base.field(key="flags", default=0, cls=int)
    public_flags: int = Base.field(key="public_flags", default=0, cls=int)
    premium: int = Base.field(key="premium_type", default=0, cls=int)

    def __str__(self) -> str:
        return f"{self.username}#{self.discriminator}"

    @property
    def mention(self) -> str:
        """The mention string to the user."""
        return f"<@{self.id}>"

    @property
    def bot(self) -> bool:
        """If the user is a bot."""
        return self.data.get("bot", False)

    @property
    def system(self) -> bool:
        """If the user is a system user."""
        return self.data.get("system", False)

    @property
    def mfa_enabled(self) -> bool:
        """If the user has 2fa enabled."""
        return self.data.get("mfa_enabled", False)

    @property
    def verified(self) -> bool:
        """If the user is verified or not."""
        return self.data.get("verified") or False
