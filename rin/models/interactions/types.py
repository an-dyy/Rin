from __future__ import annotations

import enum

__all__ = (
    "InteractionResponse",
    "InteractionType",
)


class InteractionResponse(enum.IntEnum):
    PONG = 1
    MESSAGE = 4
    DEFER_MESSAGE = 5
    DERFER_UPDATE = 6
    UPDATE = 7
    AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class InteractionType(enum.IntEnum):
    PING = 1
    COMMAND = 2
    COMPONENT = 3
    COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5
