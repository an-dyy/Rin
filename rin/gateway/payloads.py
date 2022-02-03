from __future__ import annotations

import enum
import sys
from typing import Any

from ..types import ChunkData, HeartbeatData, IdentifyData, PayloadData, ResumeData

__all__ = (
    "OPCode",
    "format",
    "IDENTIFY",
    "RESUME",
    "HEARTBEAT",
    "GUILD_MEMBERS_CHUNK",
)


class OPCode(enum.IntFlag):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


IDENTIFY: IdentifyData = {
    "op": OPCode.IDENTIFY,
    "d": {
        "token": "{0}",
        "intents": "{1}",
        "properties": {
            "$os": sys.platform,
            "$browser": "Rin 0.1.0-alpha",
            "$device": "Rin 0.1.0-alpha",
        },
    },
}

RESUME: ResumeData = {
    "op": OPCode.RESUME,
    "d": {"token": "{0}", "session_id": "{1}", "seq": "{2}"},
}

HEARTBEAT: HeartbeatData = {"op": OPCode.HEARTBEAT, "d": "{0}"}

GUILD_MEMBERS_CHUNK: ChunkData = {
    "op": OPCode.REQUEST_GUILD_MEMBERS,
    "d": {
        "guild_id": "{0}",
        "query": "{1}",
        "limit": "{2}",
        "presences": "{3}",
        "user_ids": "{4}",
        "nonce": "{5}",
    },
}


def format(payload: PayloadData, *args: Any) -> PayloadData:
    payload = payload.copy()
    for key, value in payload.items():  # type: ignore

        if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
            payload[key] = value.format(*args)

        if isinstance(value, dict):
            value: dict[Any, Any]

            for _key, _value in value.items():
                if (
                    isinstance(_value, str)
                    and _value.startswith("{")
                    and _value.endswith("}")
                ):
                    payload[key][_key] = _value.format(*args)

    return payload
