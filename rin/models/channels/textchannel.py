from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import attr

from ..base import Base
from ..cacheable import Cacheable
from .types import ChannelType

if TYPE_CHECKING:
    from ..guild import Guild

__all__ = ("TextChannel",)


@attr.s(slots=True)
class TextChannel(Base, Cacheable):
    id: int = Base.field(cls=int, repr=True)
    type: ChannelType = Base.field(default=ChannelType.GUILD_TEXT)

    guild_id: int = Base.field(cls=int, repr=True)
    guild: Guild = Base.field()

    name: str = Base.field(repr=True)
    topic: None | str = Base.field()
    nsfw: bool = Base.field(default=False, repr=True)
    position: int = Base.field(cls=int, repr=True)

    last_message_id: None | int = Base.field(cls=int)
    last_pinned_at: None | datetime = Base.field(
        key="last_pin_timestamp", constructor=datetime.fromisoformat
    )

    owner_id: None | int = Base.field(cls=int)
    parent_id: None | int = Base.field(cls=int)

    slowmode: int = Base.field(cls=int, default=0)
    overwrites: list[dict[Any, Any]] = Base.field(key="permission_overwrite")
    permissions: str = Base.field()
