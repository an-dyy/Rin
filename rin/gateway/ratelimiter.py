from __future__ import annotations

import asyncio
import typing

__all__ = ("Ratelimiter",)


class Ratelimiter:
    __slots__ = ("rate", "per", "semaphore")

    def __init__(self, rate: int, per: int) -> None:
        self.semaphore = asyncio.Semaphore(rate)
        self.rate = rate
        self.per = per

    async def sleep(self, command: typing.Coroutine[typing.Any, typing.Any, typing.Any]) -> None:
        async with self.semaphore:
            await command

            await asyncio.sleep(self.per)
