from __future__ import annotations

import enum

__all__ = ["Events"]


@enum.unique
class Events(enum.Enum):
    """An enum of all events.
    See https://discord.com/developers/docs/topics/gateway#commands-and-events
    """

    def __str__(self) -> str:
        return self.name

    UNKNOWN = enum.auto()

    HELLO = enum.auto()
    HEARTBEAT = enum.auto()
    READY = enum.auto()
    RESUMED = enum.auto()
    RECONNECT = enum.auto()
    INVALID_SESSION = enum.auto()

    CHANNEL_CREATE = enum.auto()
    CHANNEL_UPDATE = enum.auto()
    CHANNEL_DELETE = enum.auto()
    CHANNEL_PINS_UPDATE = enum.auto()

    THREAD_CREATE = enum.auto()
    THEAD_UPDATE = enum.auto()
    THREAD_DELETE = enum.auto()
    THREAD_LIST_SYNC = enum.auto()

    THREAD_MEMBER_UPDATE = enum.auto()
    THREAD_MEMBERS_UPDATE = enum.auto()

    GUILD_CREATE = enum.auto()
    GUILD_UPDATE = enum.auto()
    GUILD_DELETE = enum.auto()

    GUILD_BAN_ADD = enum.auto()
    GUILD_BAN_REMOVE = enum.auto()

    GUILD_EMOJIS_UPDATE = enum.auto()
    GUILD_STICKERS_UPDATE = enum.auto()
    GUILD_INTEGRATIONS_UPDATE = enum.auto()

    GUILD_MEMBER_ADD = enum.auto()
    GUILD_MEMBER_REMOVE = enum.auto()
    GUILD_MEMBER_UPDATE = enum.auto()
    GUILD_MEMBERS_CHUNK = enum.auto()

    GUILD_ROLE_CREATE = enum.auto()
    GUILD_ROLE_UPDATE = enum.auto()
    GUILD_ROLE_DELETE = enum.auto()

    GUILD_SCHEDULED_EVENT_CREATE = enum.auto()
    GUILD_SCHEDULED_EVENT_UPDATE = enum.auto()
    GUILD_SCHEDULED_EVENT_DELETE = enum.auto()
    GUILD_SCHEDULED_EVENT_USER_ADD = enum.auto()
    GUILD_SCHEDULED_EVENT_USER_REMOVE = enum.auto()

    INTEGRATION_CREATE = enum.auto()
    INTREGRATION_UPDATE = enum.auto()
    INTEGRATION_DELETE = enum.auto()

    INTERACTION_CREATE = enum.auto()

    INVITE_CREATE = enum.auto()
    INVITE_DELETE = enum.auto()

    MESSAGE_CREATE = enum.auto()
    MESSAGE_UPDATE = enum.auto()
    MESSAGE_DELETE = enum.auto()
    MESSAGE_DELETE_BULK = enum.auto()

    MESSAGE_REACTION_ADD = enum.auto()
    MESSAGE_REACTION_REMOVE = enum.auto()
    MESSAGE_REACTION_REMOVE_ALL = enum.auto()
    MESSAGE_REACTION_REMOVE_EMOJI = enum.auto()

    PRESENCE_UPDATE = enum.auto()

    STAGE_INSTANCE_CREATE = enum.auto()
    STAGE_INSTANCE_DELETE = enum.auto()
    STAGE_INSTANCE_UPDATE = enum.auto()

    TYPING_START = enum.auto()
    USER_UPDATE = enum.auto()

    VOICE_STATE_UPDATE = enum.auto()
    VOICE_SERVER_UPDATE = enum.auto()

    WEBHOOKS_UPDATE = enum.auto()
