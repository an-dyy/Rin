from __future__ import annotations

import enum

__all__ = (
    "ButtonStyle",
    "TextInputStyle",
    "ComponentType",
)


class ButtonStyle(enum.IntEnum):
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


class TextInputStyle(enum.IntEnum):
    SHORT = 1
    PARAGRAPH = 2


class ComponentType(enum.IntEnum):
    ACTIONROW = 1
    BUTTON = 2
    SELECTMENU = 3
    TEXTINPUT = 4
