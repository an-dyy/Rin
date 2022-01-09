from __future__ import annotations

import typing

__all__ = ("DispatchData", "IdentifyData", "ResumeData", "HeartbeatData")


class DispatchData(typing.TypedDict):
    d: dict[typing.Any, typing.Any] | int
    session_id: str

    op: int
    s: int
    t: str


class IdentifyData(typing.TypedDict):
    op: int
    d: dict[str, str | int | dict[str, str]]


class ResumeData(typing.TypedDict):
    op: int
    d: dict[str, str | int]


class HeartbeatData(typing.TypedDict):
    op: int
    d: int
