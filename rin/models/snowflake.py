from __future__ import annotations

from datetime import datetime
from typing import Any

__all__ = ("Snowflake",)


class Snowflake(int):
    """Represents a snowflake."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Snowflake:
        return super().__new__(cls, *args, **kwargs)

    @property
    def created_at(self) -> datetime:
        """The time at which the snowflake was created."""
        return datetime.fromtimestamp(((self >> 22) + 1420070400000) / 1000)
