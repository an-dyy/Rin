from __future__ import annotations

from typing import TYPE_CHECKING, Any
from datetime import datetime

import attr

from ..base import BaseModel
from ..cacheable import Cacheable
from ..user import User

from .role import Role

if TYPE_CHECKING:
    from .guild import Guild
    from ...client import GatewayClient

__all__ = ("Member",)


@attr.s(slots=True)
class Member(BaseModel, Cacheable):
    nick: None | str = BaseModel.field(None, str)
    avatar: None | str = BaseModel.field(None, str)

    deaf: bool = BaseModel.field(None, bool)
    mute: bool = BaseModel.field(None, bool)
    pending: bool = BaseModel.field(None, bool)

    def __attrs_post_init__(self) -> None:
        self.guild: Guild
        super().__attrs_post_init__()

        if self.user is not None:  # NONE WHEN IN MESSAGE_CREATE
            Member.cache.set(self.user.snowflake, self)

    @BaseModel.property("user", User)
    def user(self, client: GatewayClient, data: dict[str, Any]) -> User:
        if user := User.cache.get(int(data["id"])):
            return user

        return User(client, data)

    @BaseModel.property("roles", list[Role])
    def roles(self, _: GatewayClient, data: list[str]) -> list[Role]:
        roles: list[Role] = []

        for role_id in data:
            if role := Role.cache.get(int(role_id)):

                roles.append(role)

        return roles

    @BaseModel.property("joined_at", datetime)
    def joined_at(self, _: GatewayClient, data: str) -> datetime:
        return datetime.fromisoformat(data)

    @BaseModel.property("premium_since", datetime)
    def premium_since(self, _: GatewayClient, data: None | str) -> None | datetime:
        if data is not None:
            return datetime.fromisoformat(data)

    @BaseModel.property("communication_disabled_until", datetime)
    def timeout(self, _: GatewayClient, data: None | str) -> None | datetime:
        if data is not None:
            return datetime.fromisoformat(data)
