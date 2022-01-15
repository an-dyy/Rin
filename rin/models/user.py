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
    """

    __slots__ = ("_client", "_data")

    def __init__(self, client: GatewayClient, data: UserData) -> None:
        self._client = client
        self._data = data

    def __repr__(self) -> str:
        return f"<User username={self.username!r} discriminator={self.discriminator!r}>"

    @property
    def id(self) -> int:
        """The ID of the user."""
        return int(self._data["id"])

    @property
    def username(self) -> str:
        """The username of the user."""
        return self._data["username"]

    @property
    def discriminator(self) -> int:
        """The discriminator of the user. This is also known as the tag."""
        return int(self._data["discriminator"])

    @property
    def avatar(self) -> None | str:
        """The avatar of the user."""
        return self._data.get("avatar")

    @property
    def bot(self) -> bool:
        """If the user is a bot."""
        return self._data.get("bot") or False

    @property
    def system(self) -> bool:
        """If the user is a system user."""
        return self._data.get("system") or False

    @property
    def mfa_enabled(self) -> bool:
        """If the user has 2fa enabled."""
        return self._data.get("mfa_enabled") or False

    @property
    def banner(self) -> None | str:
        """The banner of the user."""
        return self._data.get("banner")

    @property
    def accent_color(self) -> None | int:
        """The accent color of the user."""
        color = self._data.get("accent_color")
        return int(color) if color is not None else None

    @property
    def locale(self) -> None | str:
        """The locale of the user."""
        return self._data.get("locale")

    @property
    def verified(self) -> bool:
        """If the user is verified or not."""
        return self._data.get("verified") or False

    @property
    def email(self) -> None | str:
        """The email of the user. Email scope is required"""
        return self._data.get("email")

    @property
    def flags(self) -> None | int:
        """The flags of the user."""
        flags = self._data.get("flags")
        return int(flags) if flags is not None else None

    @property
    def premium_type(self) -> None | int:
        """The premium type of the user."""
        premium_type = self._data.get("premium_type")
        return int(premium_type) if premium_type is not None else None

    @property
    def public_flags(self) -> int:
        """The public flags of the user."""
        flags = self._data.get("public_flags")
        return int(flags) if flags is not None else 0
