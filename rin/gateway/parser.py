from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr
from .event import Event

if TYPE_CHECKING:
    from ..client import GatewayClient


@attr.s(slots=True)
class Parser:
    client: GatewayClient = attr.field()

    async def no_parse(self, event: Event[Any], data: dict[Any, Any]) -> None:
        self.client.dispatch(event, data)
