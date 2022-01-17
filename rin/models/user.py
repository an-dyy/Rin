from __future__ import annotations

from typing import TYPE_CHECKING

from .cacheable import Cacheable

if TYPE_CHECKING:
    from rin.types import UserData

    from ..client import GatewayClient

__all__ = ("User",)


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

    __slots__ = (
        "_client",
        "_data",
        "id",
        "username",
        "discriminator",
        "avatar",
        "banner",
        "color",
        "locale",
        "email",
        "flags",
        "public_flags",
        "premium",
    )

    def __init__(self, client: GatewayClient, data: UserData) -> None:
        User.cache.set(self.id, self)

        self._client = client
        self._data = data

        self.id = int(data["id"])
        self.username = data["username"]
        self.discriminator = data["discriminator"]

        self.avatar = data.get("avatar")
        self.banner = data.get("banner")
        self.color = data.get("accent_color", 0)

        self.locale = data.get("locale")
        self.email = data.get("email")

        self.flags = data.get("flags", 0)
        self.public_flags = data.get("public_flags", 0)
        self.premium = self._data.get("premium_type", 0)

    def __repr__(self) -> str:
        return f"<User username={self.username!r} discriminator={self.discriminator!r}>"

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
