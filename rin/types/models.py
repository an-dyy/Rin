from __future__ import annotations

from typing import TypedDict

__all__ = ("UserData",)


class UserData(TypedDict):
    id: str
    username: str
    discriminator: str
    avatar: None | str

    bot: bool
    system: bool
    mfa_enabled: bool
    verified: bool

    banner: str
    accent_color: int

    locale: None | str
    email: None | str

    flags: int
    premium_type: int
    public_flags: int
