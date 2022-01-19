from __future__ import annotations

import asyncio
from typing import Any

import attr

__all__ = ("Ratelimiter",)


@attr.s(slots=True)
class Ratelimiter:
    rate: int = attr.field()
    per: int = attr.field()

    semaphore: asyncio.Semaphore = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.semaphore = asyncio.Semaphore(self.rate)

    async def __aenter__(self) -> Ratelimiter:
        await self.semaphore.acquire()
        return self

    async def __aexit__(self, *_: Any) -> None:
        await asyncio.sleep(self.per)
        self.semaphore.release()
