from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    Bases = tuple[type, ...]
    Attrs = dict[Any, Any]

__all__ = ("IntentsBuilder",)


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


class IntentsBuilder(metaclass=IntentsMeta):
    """A helper class for Intents.
    Creates an intent value from passed in keyword-arguments.

    .. note::

        All valid intents for :meth:`.Intents.create` are shown below but with
        lowercased names. Privileged intents are prefixed with a `!`.

    +---------------------------+---------+----------------------------------------+
    | NAME                      | VALUE   | USE                                    |
    +---------------------------+---------+----------------------------------------+
    | GUILDS                    | 1 << 0  |   - GUILD_CREATE                       |
    |                           |         |   - GUILD_UPDATE                       |
    |                           |         |   - GUILD_DELETE                       |
    |                           |         |   - GUILD_ROLE_CREATE                  |
    |                           |         |   - GUILD_ROLE_UPDATE                  |
    |                           |         |   - GUILD_ROLE_DELETE                  |
    |                           |         |   - CHANNEL_CREATE                     |
    |                           |         |   - CHANNEL_UPDATE                     |
    |                           |         |   - CHANNEL_DELETE                     |
    |                           |         |   - CHANNEL_PINS_UPDATE                |
    |                           |         |   - THREAD_CREATE                      |
    |                           |         |   - THREAD_UPDATE                      |
    |                           |         |   - THREAD_DELETE                      |
    |                           |         |   - THREAD_LIST_SYNC                   |
    |                           |         |   - THREAD_MEMBER_UPDATE               |
    |                           |         |   - THREAD_MEMBERS_UPDATE *            |
    |                           |         |   - STAGE_INSTANCE_CREATE              |
    |                           |         |   - STAGE_INSTANCE_UPDATE              |
    |                           |         |   - STAGE_INSTANCE_DELETE              |
    +---------------------------+---------+----------------------------------------+
    | !GUILD_MEMBERS            | 1 << 1  |   - GUILD_MEMBER_ADD                   |
    |                           |         |   - GUILD_MEMBER_UPDATE                |
    |                           |         |   - GUILD_MEMBER_REMOVE                |
    |                           |         |   - THREAD_MEMBERS_UPDATE *            |
    +---------------------------+---------+----------------------------------------+
    | GUILD_BANS                | 1 << 2  |   - GUILD_BAN_ADD                      |
    |                           |         |   - GUILD_BAN_REMOVE                   |
    +---------------------------+---------+----------------------------------------+
    | GUILD_EMOJIS_AND_STICKERS | 1 << 3  |   - GUILD_EMOJIS_UPDATE                |
    |                           |         |   - GUILD_STICKERS_UPDATE              |
    +---------------------------+---------+----------------------------------------+
    | GUILD_INTEGRATIONS        | 1 << 4  |   - GUILD_INTEGRATIONS_UPDATE          |
    |                           |         |   - INTEGRATION_CREATE                 |
    |                           |         |   - INTEGRATION_UPDATE                 |
    |                           |         |   - INTEGRATION_DELETE                 |
    +---------------------------+---------+----------------------------------------+
    | GUILD_WEBHOOKS            | 1 << 5  | - WEBHOOKS_UPDATE                      |
    +---------------------------+---------+----------------------------------------+
    | GUILD_INVITES             | 1 << 6  |   - INVITE_CREATE                      |
    |                           |         |   - INVITE_DELETE                      |
    +---------------------------+---------+----------------------------------------+
    | GUILD_VOICE_STATES        | 1 << 7  | - VOICE_STATE_UPDATE                   |
    +---------------------------+---------+----------------------------------------+
    | !GUILD_PRESENCES          | 1 << 8  | - PRESENCE_UPDATE                      |
    +---------------------------+---------+----------------------------------------+
    | GUILD_MESSAGES            | 1 << 9  |   - MESSAGE_CREATE                     |
    |                           |         |   - MESSAGE_UPDATE                     |
    |                           |         |   - MESSAGE_DELETE                     |
    |                           |         |   - MESSAGE_DELETE_BULK                |
    +---------------------------+---------+----------------------------------------+
    | GUILD_MESSAGE_REACTIONS   | 1 << 10 |   - MESSAGE_REACTION_ADD               |
    |                           |         |   - MESSAGE_REACTION_REMOVE            |
    |                           |         |   - MESSAGE_REACTION_REMOVE_ALL        |
    |                           |         |   - MESSAGE_REACTION_REMOVE_EMOJI      |
    +---------------------------+---------+----------------------------------------+
    | GUILD_MESSAGE_TYPING      | 1 << 11 | - TYPING_START                         |
    +---------------------------+---------+----------------------------------------+
    | DIRECT_MESSAGES           | 1 << 12 |   - MESSAGE_CREATE                     |
    |                           |         |   - MESSAGE_UPDATE                     |
    |                           |         |   - MESSAGE_DELETE                     |
    |                           |         |   - CHANNEL_PINS_UPDATE                |
    +---------------------------+---------+----------------------------------------+
    | DIRECT_MESSAGE_REACTIONS  | 1 << 13 |   - MESSAGE_REACTION_ADD               |
    |                           |         |   - MESSAGE_REACTION_REMOVE            |
    |                           |         |   - MESSAGE_REACTION_REMOVE_ALL        |
    |                           |         |   - MESSAGE_REACTION_REMOVE_EMOJI      |
    +---------------------------+---------+----------------------------------------+
    | DIRECT_MESSAGE_TYPING     | 1 << 14 |   - TYPING_START                       |
    +---------------------------+---------+----------------------------------------+
    | GUILD_SCHEDULED_EVENTS    | 1 << 16 |   - GUILD_SCHEDULED_EVENT_CREATE       |
    |                           |         |   - GUILD_SCHEDULED_EVENT_UPDATE       |
    |                           |         |   - GUILD_SCHEDULED_EVENT_DELETE       |
    |                           |         |   - GUILD_SCHEDULED_EVENT_USER_ADD     |
    |                           |         |   - GUILD_SCHEDULED_EVENT_USER_REMOVE  |
    +---------------------------+---------+----------------------------------------+
    """

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

        self.guilds: bool
        self.guild_bans: bool
        self.guild_members: bool
        self.guild_bans: bool

        self.guild_emojis_and_stickers: bool
        self.guild_integrations: bool
        self.guild_webhooks: bool
        self.guild_invites: bool

        self.guild_voice_states: bool
        self.guild_presences: bool

        self.guild_message: bool
        self.guild_message_reactions: bool
        self.guild_message_typing: bool

        self.direct_messages: bool
        self.direct_message_reactions: bool
        self.direct_message_typing: bool

        self.guild_scheduled_events: bool

    @classmethod
    def create(cls: type[IntentsBuilder], **kwargs: bool) -> IntentsBuilder:
        """Creates an intents instance with a value specific to
        the passed in keyword-arguments.

        Examples
        --------
        .. code:: python

            intents = Intents.create(guild_members=True)

        Parameters
        ----------
        kwargs: :class:`bool`
            Keyword-arguments specific to the Intent with True/False value.

        Returns
        -------
        :class:`.Intents`
            A created intents instance with a value corresponding to the keyword-arguments passed.
        """
        intents: dict[str, int] = cls.__intents__

        self = cls(0)

        for intent in intents:
            setattr(self, intent, False)

        for attr, value in kwargs.items():
            intent = intents.get(attr)

            if intent is None:
                raise ValueError(f"{attr!r} is not a valid intent.")

            if value is True:
                self.value |= intent
                setattr(self, attr, value)

            elif value is False:
                self.value &= ~intent

        return self

    @classmethod
    def default(cls: type[IntentsBuilder], **kwargs: bool) -> IntentsBuilder:
        """Creates an intents instance without privileged intents.

        Parameters
        ----------
        kwargs: class:`bool`
            Extra intents to create along side the default ones.

        Returns
        -------
        :class:`.Intents`
            A created intents instance with the corresponding value.
        """
        return cls.create(
            **kwargs,
            guilds=True,
            guild_bans=True,
            guild_emojis_and_stickers=True,
            guild_integrations=True,
            guild_webhooks=True,
            guild_invites=True,
            guild_voice_states=True,
            guild_messages=True,
            guild_message_reactions=True,
            guild_message_typing=True,
            direct_messages=True,
            direct_message_reactions=True,
            direct_message_typing=True,
            guild_scheduled_events=True,
        )

    @classmethod
    def privileged(cls: type[IntentsBuilder], **kwargs: bool) -> IntentsBuilder:
        """Creates an intents instance with only privileged intents.

        Parameters
        ----------
        kwargs: class:`bool`
            Extra intents to create along side the privileged ones.

        Returns
        -------
        :class:`.Intents`
            A created intents instance with the corresponding value.

        """
        return cls.create(**kwargs, guild_members=True, guild_presences=True)

    @classmethod
    def none(cls: type[IntentsBuilder]) -> IntentsBuilder:
        """Creates an intents instance without any intents.

        Returns
        -------
        :class:`.Intents`
            A created intents instance with no value.
        """
        return cls(0)
