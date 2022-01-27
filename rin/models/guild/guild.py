from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import attr

from ..base import Base
from ..cacheable import Cacheable
from ..channels import TextChannel

if TYPE_CHECKING:
    Check = Callable[..., bool]

text_check: Check = lambda c: c["type"] == 0


@attr.s(slots=True)
class Guild(Base, Cacheable):
    id: int = Base.field(cls=int, repr=True)

    text_channels: list[TextChannel] = Base.field(
        cls=TextChannel, check=text_check, has_client=True, key="channels"
    )

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()

        for channel in self.text_channels:
            channel.guild = self
