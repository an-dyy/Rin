from __future__ import annotations

from typing import TypedDict

__all__ = ("UserData",)


class UserData(TypedDict):
    id: str
    username: str
    discriminator: str
    avatar: None | str
    bot: None | bool
    system: None | bool
    mfa_enabled: None | bool
    banner: None | str
    accent_color: None | int
    locale: None | str
    verified: None | bool
    email: None | str
    flags: None | str
    premium_type: None | int
    public_flags: None | int
