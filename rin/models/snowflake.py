from __future__ import annotations

from datetime import datetime
from typing import Protocol

__all__ = ("Snowflake",)


class Snowflake(Protocol):
    """A snowflake protocol.

    Attributes
    ----------
    id: :class:`int`
        The snowflake.

    """

    __slots__ = ()
    id: int

    @property
    def created_at(self) -> datetime:
        """The date at which the snowflake was created.
        See https://discord.com/developers/docs/reference#snowflakes for more info.
        """
        return datetime.fromtimestamp(((self.id >> 22) + 1420070400000) / 1000)
