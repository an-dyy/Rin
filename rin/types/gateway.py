from __future__ import annotations

from typing import Any, TypedDict

__all__ = ("DispatchData", "IdentifyData", "ResumeData", "HeartbeatData", "ChunkData")


class DispatchData(TypedDict):
    d: dict[Any, Any] | int
    session_id: str

    op: int
    s: int
    t: str


class IdentifyData(TypedDict):
    op: int
    d: dict[str, str | int | dict[str, str]]


class ResumeData(TypedDict):
    op: int
    d: dict[str, str | int]


class HeartbeatData(TypedDict):
    op: int
    d: int


class ChunkData(TypedDict):
    op: int
    d: dict[str, str | int | list[int] | None]
