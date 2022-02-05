from typing import Literal, TypedDict, Any
from typing_extensions import Required

__all__ = (
    "Payload",
    "IdentifyInner",
    "IdentifyPayload",
    "ResumerInner",
    "ResumePayload",
    "HeartbeatPayload",
    "ChunkInner",
    "ChunkPayload",
    "DispatchPayload",
)

class Payload(TypedDict):
    op: int
    d: dict[Any, Any]
    s: None | int
    t: None | str

class IdentifyInner(TypedDict, total=False):
    token: Required[str]
    intents: Required[int]
    properties: Required[dict[str, str]]
    compress: bool
    large_threshold: int
    shards: list[tuple[int, int]]
    presences: list[dict[Any, Any]]  # TODO: Actual types

class IdentifyPayload(TypedDict):
    op: Literal[2]
    d: IdentifyInner

class ResumerInner(TypedDict):
    token: str
    session_id: str
    seq: int

class ResumePayload(TypedDict):
    op: Literal[6]
    d: ResumerInner

class HeartbeatPayload(TypedDict):
    op: Literal[1]
    d: int

class ChunkInner(TypedDict, total=False):
    guild_id: Required[int]
    query: Required[str]
    limit: Required[int]
    presences: bool
    user_ids: int | list[int]
    nonce: None | str

class ChunkPayload(TypedDict):
    op: Literal[8]
    d: ChunkInner

DispatchPayload = IdentifyPayload | ResumePayload | HeartbeatPayload | ChunkPayload
