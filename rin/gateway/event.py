from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Generic, Literal, Any, overload, Callable

import asyncio
import attr

from ..models import User

if TYPE_CHECKING:
    Timeout = None | float
    Check = Callable[..., bool]

    from .dispatch import Collector, Listener

__all__ = ("Event", "Events")
T = TypeVar(
    "T",
    bound=Literal[
        "*",
        "READY",
        "CHANNEL_CREATE",
        "CHANNEL_UPDATE",
        "CHANNEL_DELETE",
        "CHANNEL_PINS_UPDATE",
        "THREAD_CREATE",
        "THREAD_UPDATE",
        "THREAD_DELETE",
        "THREAD_LIST_SYNC",
        "THREAD_MEMBER_UPDATE",
        "THREAD_MEMBERS_UPDATE",
        "GUILD_CREATE",
        "GUILD_UPDATE",
        "GUILD_DELETE",
        "GUILD_BAN_ADD",
        "GUILD_BAN_REMOVE",
        "GUILD_EMOJIS_UPDATE",
        "GUILD_STICKERS_UPDATE",
        "GUILD_INTEGRATIONS_UPDATE",
        "GUILD_MEMBER_ADD",
        "GUILD_MEMBER_REMOVE",
        "GUILD_MEMBER_UPDATE",
        "GUILD_MEMBERS_CHUNK",
        "GUILD_ROLE_CREATE",
        "GUILD_ROLE_UPDATE",
        "GUILD_ROLE_DELETE",
        "GUILD_SCHEDULED_EVENT_CREATE",
        "GUILD_SCHEDULED_EVENT_UPDATE",
        "GUILD_SCHEDULED_EVENT_DELETE",
        "GUILD_SCHEDULED_EVENT_USER_ADD",
        "GUILD_SCHEDULED_EVENT_USER_REMOVE",
        "INTEGRATION_CREATE",
        "INTEGRATION_UPDATE",
        "INTEGRATION_DELETE",
        "INVITE_CREATE",
        "INVITE_DELETE",
        "MESSAGE_CREATE",
        "MESSAGE_UPDATE",
        "MESSAGE_DELETE",
        "MESSAGE_DELETE_BULK",
        "MESSAGE_REACTION_ADD",
        "MESSAGE_REACTION_REMOVE",
        "MESSAGE_REACTION_REMOVE_ALL",
        "MESSAGE_REACTION_REMOVE_EMOJI",
        "PRESENCE_UPDATE",
        "STAGE_INSTANCE_CREATE",
        "STAGE_INSTANCE_UPDATE",
        "STAGE_INSTANCE_DELETE",
        "TYPING_START",
        "VOICE_STATE_UPDATE",
        "VOICE_SERVER_UPDATE",
        "WEBHOOKS_UPDATE",
    ],
)


@attr.s(slots=True)
class Event(Generic[T]):
    name: T = attr.field()

    futures: list[tuple[asyncio.Future[Any], Callable[..., bool]]] = attr.field(
        init=False
    )

    listeners: list[Listener] = attr.field(init=False)
    collectors: list[Collector] = attr.field(init=False)
    temp: list[Listener] = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.futures: list[tuple[asyncio.Future[Any], Callable[..., bool]]] = []

        self.listeners: list[Listener] = []
        self.collectors: list[Collector] = []
        self.temp: list[Listener] = []

    def __str__(self) -> str:
        return self.name

    @overload
    async def wait(
        self: Event[Literal["*"]],
        timeout: None | float = None,
        check: Check = lambda *_: True,
    ) -> tuple[Event[Any], dict[Any, Any]]:
        ...

    @overload
    async def wait(
        self: Event[Literal["READY"]],
        timeout: None | float = None,
        check: Check = lambda *_: True,
    ) -> User:
        ...

    async def wait(
        self, timeout: None | float = None, check: Check = lambda *_: True
    ) -> Any:
        future = asyncio.get_running_loop().create_future()
        self.futures.append((future, check))

        return await asyncio.wait_for(future, timeout=timeout)


class Events:
    WILDCARD = Event("*")
    READY = Event("READY")

    CHANNEL_CREATE = Event("CHANNEL_CREATE")
    CHANNEL_UPDATE = Event("CHANNEL_UPDATE")
    CHANNEL_DELETE = Event("CHANNEL_DELETE")
    CHANNEL_PINS_UPDATE = Event("CHANNEL_PINS_UPDATE")

    THREAD_CREATE = Event("THREAD_CREATE")
    THREAD_UPDATE = Event("THREAD_UPDATE")
    THREAD_DELETE = Event("THREAD_DELETE")
    THREAD_LIST_SYNC = Event("THREAD_LIST_SYNC")
    THREAD_MEMBER_UPDATE = Event("THREAD_MEMBER_UPDATE")
    THREAD_MEMBERS_UPDATE = Event("THREAD_MEMBERS_UPDATE")

    GUILD_CREATE = Event("GUILD_CREATE")
    GUILD_UPDATE = Event("GUILD_UPDATE")
    GUILD_DELETE = Event("GUILD_DELETE")

    GUILD_BAN_ADD = Event("GUILD_BAN_ADD")
    GUILD_BAN_REMOVE = Event("GUILD_BAN_REMOVE")

    GUILD_EMOJIS_UPDATE = Event("GUILD_EMOJIS_UPDATE")
    GUILD_STICKERS_UPDATE = Event("GUILD_STICKERS_UPDATE")
    GUILD_INTEGRATIONS_UPDATE = Event("GUILD_INTEGRATIONS_UPDATE")

    GUILD_MEMBER_ADD = Event("GUILD_MEMBER_ADD")
    GUILD_MEMBER_REMOVE = Event("GUILD_MEMBER_REMOVE")
    GUILD_MEMBER_UPDATE = Event("GUILD_MEMBER_UPDATE")
    GUILD_MEMBERS_CHUNK = Event("GUILD_MEMBERS_CHUNK")

    GUILD_ROLE_CREATE = Event("GUILD_ROLE_CREATE")
    GUILD_ROLE_UPDATE = Event("GUILD_ROLE_UPDATE")
    GUILD_ROLE_DELETE = Event("GUILD_ROLE_DELETE")

    GUILD_SCHEDULED_EVENT_CREATE = Event("GUILD_SCHEDULED_EVENT_CREATE")
    GUILD_SCHEDULED_EVENT_UPDATE = Event("GUILD_SCHEDULED_EVENT_UPDATE")
    GUILD_SCHEDULED_EVENT_DELETE = Event("GUILD_SCHEDULED_EVENT_DELETE")
    GUILD_SCHEDULED_EVENT_USER_ADD = Event("GUILD_SCHEDULED_EVENT_USER_ADD")
    GUILD_SCHEDULED_EVENT_USER_REMOVE = Event("GUILD_SCHEDULED_EVENT_USER_REMOVE")

    INTEGRATION_CREATE = Event("INTEGRATION_CREATE")
    INTEGRATION_UPDATE = Event("INTEGRATION_UPDATE")
    INTEGRATION_DELETE = Event("INTEGRATION_DELETE")

    INVITE_CREATE = Event("INVITE_CREATE")
    INVITE_DELETE = Event("INVITE_DELETE")

    MESSAGE_CREATE = Event("MESSAGE_CREATE")
    MESSAGE_UPDATE = Event("MESSAGE_UPDATE")
    MESSAGE_DELETE = Event("MESSAGE_DELETE")
    MESSAGE_DELETE_BULK = Event("MESSAGE_DELETE_BULK")

    MESSAGE_REACTION_ADD = Event("MESSAGE_REACTION_ADD")
    MESSAGE_REACTION_REMOVE = Event("MESSAGE_REACTION_REMOVE")
    MESSAGE_REACTION_REMOVE_ALL = Event("MESSAGE_REACTION_REMOVE_ALL")
    MESSAGE_REACTION_REMOVE_EMOJI = Event("MESSAGE_REACTION_REMOVE_EMOJI")

    PRESENCE_UPDATE = Event("PRESENCE_UPDATE")

    STAGE_INSTANCE_CREATE = Event("STAGE_INSTANCE_CREATE")
    STAGE_INSTANCE_DELETE = Event("STAGE_INSTANCE_DELETE")
    STAGE_INSTANCE_UPDATE = Event("STAGE_INSTANCE_UPDATE")

    TYPING_START = Event("TYPING_START")

    VOICE_STATE_UPDATE = Event("VOICE_STATE_UPDATE")
    VOICE_SERVER_UPDATE = Event("VOICE_SERVER_UPDATE")

    WEBHOOKS_UPDATE = Event("WEBHOOKS_UPDATE")
