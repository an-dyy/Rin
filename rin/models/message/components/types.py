from __future__ import annotations

import enum

__all__ = (
    "ButtonStyle",
    "ComponentType",
)


class ButtonStyle(enum.IntEnum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class ComponentType(enum.IntEnum):
    ACTIONROW = 1
    BUTTON = 2
    SELECTMENU = 3
    TEXTINPUT = 4
