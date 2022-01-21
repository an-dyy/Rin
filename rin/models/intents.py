from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    Bases = tuple[type, ...]
    Attrs = dict[Any, Any]

__all__ = ("Intents",)


class IntentsMeta(type):
    __value__: int

    def __new__(
        cls: type[IntentsMeta], name: str, bases: Bases, attrs: Attrs
    ) -> IntentsMeta:
        intents: dict[str, int] = {}

        for attr, value in attrs.copy().items():
            if attr.startswith("_") or isinstance(value, classmethod):
                continue

            intents[attr.lower()] = value

        attrs["__intents__"] = intents
        return super().__new__(cls, name, bases, attrs)


class Intents(metaclass=IntentsMeta):
    __intents__: dict[str, int]

    NONE = 0

    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2

    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6

    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8

    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11

    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14

    GUILD_SCHEDULED_EVENTS = 1 << 16

    def __init__(self, value: int = 0) -> None:
        self.value: int = value

    @classmethod
    def create(cls: type[Intents], value: int = 0, **kwargs: bool) -> Intents:
        intents: dict[str, int] = cls.__intents__

        self = cls(value)
        self.value = value

        for attr, value in kwargs.items():
            intent = intents.get(attr)

            if intent is None:
                raise ValueError(f"{attr!r} is not a valid intent.")

            if value is True:
                self.value |= intent

            elif value is False:
                self.value &= ~intent

        return self

    @classmethod
    def default(cls: type[Intents]) -> Intents:
        self = cls.create()

        for intent, value in self.__intents__.items():
            if intent == "guild_presences" or intent == "guild_members":
                continue

            self.value |= value

        return self

    @classmethod
    def privileged(cls: type[Intents]) -> Intents:
        return cls.create(guild_members=True, guild_presences=True)

    @classmethod
    def none(cls: type[Intents]) -> Intents:
        return cls(0)
