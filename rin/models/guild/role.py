from __future__ import annotations

from typing import Any, TypedDict

import attr

from ..base import BaseModel
from ..cacheable import Cacheable
from ..snowflake import Snowflake

__all__ = ("Role",)


class RoleTags(TypedDict, total=False):
    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: None


@attr.s(slots=True)
class Role(BaseModel, Cacheable):
    """Represents a Role object.

    Attributes
    ----------
    snowflake: :class:`.Snowflake`
        The snowflake of the role.

    name: :class:`str`
        The name of the role.

    color: :class:`int`
        The color of the role.

    hoist: :class:`bool`
        If the role is hoisted.

    position: :class:`int`
        The position of the role in the guild.

    permissions: :class:`str`
        The permissions of the role.

    icon: None | :class:`str`
        The icon hash of the role.

    emoji: None | :class:`str`
        The unicode emoji of the role.

    managed: :class:`bool`
        If the role is managed by an integration.

    mentionable: :class:`bool`
        If the role is mentionable.

    tags: :class:`.RoleTags`
        The tags of the role.
    """

    snowflake: Snowflake = BaseModel.field("id", Snowflake, repr=True)
    name: str = BaseModel.field(None, str, repr=True)

    color: int = BaseModel.field(None, int)
    hoist: bool = BaseModel.field(None, bool)
    position: int = BaseModel.field(None, int, repr=True)
    permissions: str = BaseModel.field(None, str)

    icon: None | str = BaseModel.field(None, str)
    emoji: None | str = BaseModel.field("unicode_emoji", str)

    managed: bool = BaseModel.field(None, bool)
    mentionable: bool = BaseModel.field(None, bool)
    tags: RoleTags = BaseModel.field(None, dict[str, Any])

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        Role.cache.set(self.snowflake, self)
