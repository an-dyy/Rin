from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from .. import Base, Cacheable
from ..channels import TextChannel

if TYPE_CHECKING:
    from ...client import GatewayClient


def create_channels(data: dict[Any, Any], client: GatewayClient):
    type: int = data["type"]

    if type == 0:
        return TextChannel(client, data)


@attr.s(slots=True)
class Guild(Base, Cacheable):
    id: int = Base.field(cls=int)
    channels: list[TextChannel] = Base.field(cls=TextChannel, has_client=True)
