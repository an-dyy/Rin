from __future__ import annotations

from datetime import datetime
from typing import Any

import attr

from .. import Base, Cacheable, TextChannel, User

__all__ = ("Message",)


@attr.s(slots=True)
class Message(Base, Cacheable, max=1000):
    id: int = Base.field(cls=int, repr=True)
    channel: TextChannel = Base.field()

    channel_id: int = Base.field(cls=int, repr=True)
    guild_id: int = Base.field(cls=int)

    user: User = Base.field(cls=User)
    member: dict[Any, Any] = Base.field()

    content: str = Base.field()
    timestamp: datetime = Base.field(constructor=datetime.fromisoformat)
    editted_timestamp: datetime = Base.field(constructor=datetime.fromisoformat)

    tts: bool = Base.field()
    mentioned_everyone = Base.field(key="mention_everyone")

    mentions: list[User] = Base.field(cls=User)
    mentioned_roles: list[dict[Any, Any]] = Base.field()
    mentioned_channels: list[dict[Any, Any]] = Base.field()

    referenced: None | dict[Any, Any] = Base.field(key="referenced_message")

    thread: None | dict[Any, Any] = Base.field()
    attachments: list[dict[Any, Any]] = Base.field()
    embeds: list[dict[Any, Any]] = Base.field()
    reactions: list[dict[Any, Any]] = Base.field()
    activity: dict[Any, Any] = Base.field()

    nonce: None | str = Base.field()
    pinned: bool = Base.field()

    webhook_id: None | int = Base.field(cls=int)
    application_id: None | int = Base.field(cls=int)
    application: None | dict[Any, Any] = Base.field()

    type: int = Base.field(cls=int)
    flags: None | int = Base.field(cls=int)

    interaction: None | dict[Any, Any] = Base.field()
    components: None | list[dict[Any, Any]] = Base.field()

    stickers: None | list[dict[Any, Any]] = Base.field(key="sticker_items")

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        self.channel = TextChannel.cache[self.channel_id]  # type: ignore
