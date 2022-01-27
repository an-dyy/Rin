from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ..base import Base
from ..cacheable import Cacheable
from ..channels import TextChannel

if TYPE_CHECKING:
    from ...client import GatewayClient


def create_channels(client: GatewayClient, data: dict[Any, Any]) -> Any:
    type: int = data["type"]

    if type == 0:
        return TextChannel(client, data)


@attr.s(slots=True)
class Guild(Base, Cacheable):
    id: int = Base.field(cls=int)
    channels: list[TextChannel] = Base.field(
        constructor=create_channels, has_client=True
    )
