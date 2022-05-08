from __future__ import annotations

from typing import TYPE_CHECKING

import attr

from ..base import BaseModel
from ..cacheable import Cacheable
from ..snowflake import Snowflake
from ..user import User
from .role import Role

if TYPE_CHECKING:
    from ...client import GatewayClient

__all__ = ("Emoji", "PartialEmoji")


@attr.s(slots=True)
class Emoji(BaseModel, Cacheable):
    """Represents an Emoji object.

    Attributes
    ----------
    snowflake: :class:`.Snowflake`
        The snowflake of the emoji.

    name: :class:`str`
        The name of the emoji.

    user: :class:`.User`
        The user who created the meoji.

    require_colons: :class:`bool`
        If this emoji is required to be wrapped by colons.

    managed: :class:`bool`
        If this emoji is managed.

    animated: :class:`bool`
        If this emoji is animated.

    available: :class:`bool`
        If this emoji is available.

    roles: :class:`list`
        A list of :class:`.Role` instances that can use the emoji.
    """

    snowflake: Snowflake = BaseModel.field("id", Snowflake, repr=True)
    name: str = BaseModel.field(None, str, repr=True)
    user: User = BaseModel.field(None, User)

    require_colons: bool = BaseModel.field(None, bool)
    managed: bool = BaseModel.field(None, bool)
    animated: bool = BaseModel.field(None, bool, repr=True)
    available: bool = BaseModel.field(None, bool)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        Emoji.cache.set(self.snowflake, self)

    @BaseModel.property("roles", list[Role])
    def roles(self, _: GatewayClient, data: list[str]) -> list[Role]:
        roles: list[Role] = []

        for role_id in data:
            if role := Role.cache.get(int(role_id)):
                roles.append(role)

            continue

        return roles


@attr.s(slots=True)
class PartialEmoji:
    """A partial emoji class.

    Attributes
    ----------
    name: :class:`str`
        The name of the emoji.

    id: :class:`int`
        The ID of the emoji.

    animated: :class:`bool`
        If the emoji is animated.
    """

    name: str = attr.field()
    id: int = attr.field()
    animated: bool = attr.field()
