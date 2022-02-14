from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr
from .event import Event, Events

from ..models import User

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
