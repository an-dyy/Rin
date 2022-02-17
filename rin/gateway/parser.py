from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ..models import ComponentCache, Guild, Interaction, InteractionType, Message, User
from .event import Event, Events

if TYPE_CHECKING:
    from ..client import GatewayClient


@attr.s(slots=True)
class Parser:
    """The gateway parser.
    Used for parsing the raw data received from the gateway,
    then later dispatching the event corresponding to the parser.

    Attributes
    ----------
    client: :class:`.GatewayClient`
        The client using the parser.
    """

    client: GatewayClient = attr.field()

    async def no_parse(self, event: Event[Any], data: dict[Any, Any]) -> None:
        """The default parser.

        Paramters
        ---------
        event: :class:`.Event`
            The event to dispatch after parsing.

        data: :class:`dict`
            The data to dispath with.
        """
        self.client.dispatch(event, data)

    async def parse_ready(self, data: dict[Any, Any]) -> None:
        """Parses the `READY` event.
        Dispatches a :class:`.User` object.

        Parameters
        ----------
        data: :class:`dict`
            The data from the event.
        """
        user = User(self.client, data["user"])
        self.client.user = user

        self.client.dispatch(Events.READY, user)

    async def parse_interaction_create(self, data: dict[Any, Any]) -> None:
        """Parses the `INTERACTION_CREATE` event.
        Dispatches a :class:`.Interaction` object

        Parameters
        ----------
        data: :class:`dict`
            The data from the event.
        """
        interaction = Interaction(self.client, data)

        if interaction.type is InteractionType.COMPONENT:
            if component := ComponentCache.cache.get(
                interaction.actual_data["custom_id"]
            ):
                await component.callback(interaction, component)

        self.client.dispatch(Events.INTERACTION_CREATE, interaction)

    async def parse_message_create(self, data: dict[Any, Any]) -> None:
        """Parses the `MESSAGE_CREATE` event.
        Dispatches a :class:`.Message` object

        Parameters
        ----------
        data: :class:`dict`
            The data from the event.
        """
        self.client.dispatch(Events.MESSAGE_CREATE, Message(self.client, data))

    async def parse_guild_create(self, data: dict[Any, Any]) -> None:
        """Parses the `GUILD_CREATE` event.
        Dispatches a :class:`.Guild` object

        Parameters
        ----------
        data: :class:`dict`
            The data from the event.
        """
        self.client.dispatch(Events.GUILD_CREATE, Guild(self.client, data))
