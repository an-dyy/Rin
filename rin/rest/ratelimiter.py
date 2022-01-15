from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp

from .errors import HTTPException

if TYPE_CHECKING:
    from .handler import RESTClient, Route


__all__ = ("Ratelimiter", "RatelimitedClientResponse")
_log = logging.getLogger(__name__)


class Ratelimiter:
    def __init__(self, rest: RESTClient, route: Route) -> None:
        self.loop = rest.client.loop
        self.rest = rest
        self.route = route

        self.endpoint = route.endpoint
        self.bucket = route.bucket

        self.auth = {"Authorization": f"Bot {self.rest.token}"}

    async def ensure(self) -> asyncio.Semaphore:
        if semaphore := self.get(self.bucket):
            return semaphore

        resp: RatelimitedClientResponse = await self.rest._request(
            "HEAD", self.endpoint
        )

        semaphore = asyncio.Semaphore(resp.limit)
        self.rest.semaphores[self.bucket] = semaphore

        return semaphore

    def get(self, bucket: str) -> None | asyncio.Semaphore:
        return self.rest.semaphores.get(bucket)

    async def request(self, method: str, **kwargs: Any) -> None | dict[Any, Any] | str:
        semaphore = await self.ensure()

        async with self.rest.semaphores["global"]:
            await semaphore.acquire()
            await self.route.lock.acquire()

            resp = await self.rest._request(method, self.endpoint, **kwargs)
            data: dict[Any, Any] | str = await resp.data()

            if resp.is_depleted:
                _log.debug(f"BUCKET DEPLETED: {self.bucket} RETRY: {resp.reset_after}s")

                self.loop.call_later(resp.reset_after, self.route.lock.release)
                self.loop.call_later(resp.reset_after, semaphore.release)

                await asyncio.sleep(resp.reset_after)
                return await self.request(method, **kwargs)

            if resp.ok:
                _log.debug(
                    f"{resp.status}: {method} ROUTE: {self.endpoint} REMAINING: {resp.uses}"
                )
                return data

            if resp.is_ratelimited:
                retry_after = await resp.retry_after()
                _log.debug(
                    f"RATELIMITED: {method} ROUTE: {self.endpoint} RETRY AFTER: {retry_after}"
                )

                if retry_after is not None:
                    await asyncio.sleep(retry_after)

                return await self.request(method, **kwargs)

            if not resp.ok:
                raise self.rest.ERRORS.get(resp.status, HTTPException)(data) from None

        return None

    async def __aenter__(self) -> Ratelimiter:
        return self

    async def __aexit__(self, *_: Any) -> None:
        self.rest.semaphores.pop(self.bucket, None)


class RatelimitedClientResponse(aiohttp.ClientResponse):
    REMAINING: ClassVar[str] = "X-Ratelimit-Remaining"
    RESET_AT: ClassVar[str] = "X-Ratelimit-Reset-After"
    TOTAL: ClassVar[str] = "X-Ratelimit-Limit"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def data(self) -> Any:
        try:
            return await self.json()
        except aiohttp.ContentTypeError:
            return await self.text()

    @property
    def uses(self) -> int:
        return int(self.headers.get(RatelimitedClientResponse.REMAINING, 1))

    @property
    def limit(self) -> int:
        return int(self.headers.get(RatelimitedClientResponse.TOTAL, 1))

    @property
    def reset_after(self) -> float:
        return float(self.headers.get(RatelimitedClientResponse.RESET_AT, 0))

    async def retry_after(self) -> None | float:
        return (await self.json())["retry_after"] if self.is_ratelimited else None

    @property
    def is_depleted(self) -> bool:
        return self.status != 429 and self.uses == 0

    @property
    def is_ratelimited(self) -> bool:
        return bool(self.status == 429)
