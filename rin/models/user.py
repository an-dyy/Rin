from __future__ import annotations

from typing import TYPE_CHECKING

from .cacheable import Cacheable

if TYPE_CHECKING:
    from rin.types import UserData

    from ..gateway import GatewayClient


class User(Cacheable, max=1000):
    __slots__ = ("_client", "_data")

    def __init__(self, client: GatewayClient, data: UserData) -> None:
        self._client = client
        self._data = data

    def __repr__(self) -> str:
        return f"<User username={self.username!r} discriminator={self.discriminator!r}>"

    @property
    def id(self) -> int:
        return int(self._data["id"])

    @property
    def username(self) -> str:
        return self._data["username"]

    @property
    def discriminator(self) -> int:
        return int(self._data["discriminator"])

    @property
    def avatar(self) -> None | str:
        return self._data.get("avatar")

    @property
    def bot(self) -> bool:
        return self._data.get("bot") or False

    @property
    def system(self) -> bool:
        return self._data.get("system") or False

    @property
    def mfa_enabled(self) -> bool:
        return self._data.get("mfa_enabled") or False

    @property
    def banner(self) -> None | str:
        return self._data.get("banner")

    @property
    def accent_color(self) -> None | int:
        color = self._data.get("accent_color")
        return int(color) if color is not None else None

    @property
    def locale(self) -> None | str:
        return self._data.get("locale")

    @property
    def verified(self) -> bool:
        return self._data.get("verified") or False

    @property
    def email(self) -> None | str:
        return self._data.get("email")

    @property
    def flags(self) -> None | int:
        flags = self._data.get("flags")
        return int(flags) if flags is not None else None

    @property
    def premium_type(self) -> None | int:
        premium_type = self._data.get("premium_type")
        return int(premium_type) if premium_type is not None else None

    @property
    def public_flags(self) -> int:
        flags = self._data.get("public_flags")
        return int(flags) if flags is not None else 0


User.cache.type = User
