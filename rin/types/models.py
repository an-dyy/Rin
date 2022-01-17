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
    banner: str
    accent_color: None | int
    locale: None | str
    verified: bool
    email: None | str
    flags: None | str
    premium_type: int
    public_flags: int
