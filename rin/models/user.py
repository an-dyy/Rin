from __future__ import annotations

from typing import TYPE_CHECKING

import attr

from .cacheable import Cacheable

if TYPE_CHECKING:
    from rin.types import UserData

    from ..client import GatewayClient

__all__ = ("User",)


@attr.s(slots=True)
class User(Cacheable, max=1000):
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

    _client: GatewayClient = attr.field()
    _data: UserData = attr.field()

    id: int = attr.field(init=False)
    username: str = attr.field(init=False)
    discriminator: str = attr.field(init=False)

    avatar: None | str = attr.field(init=False)
    banner: None | str = attr.field(init=False)
    color: int = attr.field(init=False)

    locale: None | str = attr.field(init=False)
    email: None | str = attr.field(init=False)

    flags: int = attr.field(init=False)
    public_flags: int = attr.field(init=False)
    premium: int = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.id = int(self._data["id"])
        self.username = self._data["username"]
        self.discriminator = self._data["discriminator"]

        self.avatar = self._data.get("avatar")
        self.banner = self._data.get("banner")
        self.color = self._data.get("accent_color", 0)

        self.locale = self._data.get("locale")
        self.email = self._data.get("email")

        self.flags = self._data.get("flags", 0)
        self.public_flags = self._data.get("public_flags", 0)
        self.premium = self._data.get("premium_type", 0)

        User.cache.set(self.id, self)

    def __str__(self) -> str:
        return f"{self.username}#{self.discriminator}"

    @property
    def mention(self) -> str:
        """The mention string to the user."""
        return f"<@{self.id}>"

    @property
    def bot(self) -> bool:
        """If the user is a bot."""
        return self._data.get("bot", False)

    @property
    def system(self) -> bool:
        """If the user is a system user."""
        return self._data.get("system", False)

    @property
    def mfa_enabled(self) -> bool:
        """If the user has 2fa enabled."""
        return self._data.get("mfa_enabled", False)

    @property
    def verified(self) -> bool:
        """If the user is verified or not."""
        return self._data.get("verified") or False
