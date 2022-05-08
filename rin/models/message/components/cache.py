from __future__ import annotations

from typing import TYPE_CHECKING

from ...cacheable import Cache, Cacheable

if TYPE_CHECKING:
    from .actionrow import Component

__all__ = ("ComponentCache",)


class ComponentCache(Cacheable):
    """A components cache."""

    cache: Cache[Component]
