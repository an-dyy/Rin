from __future__ import annotations

import asyncio
import json
import logging
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp
import attr
from multidict import istr

from .errors import HTTPException

if TYPE_CHECKING:
    from .handler import RESTClient, Route


__all__ = ("Ratelimiter", "RatelimitedClientResponse")
_log = logging.getLogger(__name__)


@attr.s(slots=True)
class Ratelimiter:
    """A class used for ratelimit handling.

    Parameters
    ----------
    rest: :class:`.RESTClient`
        The RESTClient to ratelimit.

    route: :class:`.Route`
        The route being used for the request.

    Attributes
    ----------
    loop: :class:`asyncio.AbstractEventLoop`
        The loop used for asynchronus operations.

    rest: :class:`.RESTClient`
        The RESTClient being ratelimited.

    route: :class:`.Route`
        The route being used for the request.

    endpoint: :class:`str`
        The endpoint of the Route.

    bucket: :class:`str`
        The bucket of the Route.

    auth: dict[str, str]
        The authorization header dict.
    """

    rest: RESTClient = attr.field()
    route: Route = attr.field()

    loop: asyncio.AbstractEventLoop = attr.field(init=False)
    auth: dict[str, str] = attr.field(init=False)

    endpoint: str = attr.field(init=False)
    bucket: str = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        assert self.rest.client.loop is not None

        self.loop = self.rest.client.loop
        self.auth = {"Authorization": f"Bot {self.rest.token}"}
        self.endpoint = self.route.endpoint
        self.bucket = self.route.bucket

    async def ensure(self) -> asyncio.Semaphore:
        """Ensures there is a :class:`asyncio.Semaphore`."""
        if semaphore := self.get(self.bucket):
            return semaphore

        resp: RatelimitedClientResponse = await self.rest._request("HEAD", self.endpoint)

        semaphore = asyncio.Semaphore(resp.limit)
        self.rest.semaphores[self.bucket] = semaphore

        return semaphore

    def get(self, bucket: str) -> None | asyncio.Semaphore:
        """Gets the bucket's semaphore if one exists.

        Parameters
        ----------
        bucket: :class:`str`
            The bucket to search for.

        Returns
        -------
        Optional[:class:`asyncio.Semaphore`]
            The semaphore if found.
        """
        return self.rest.semaphores.get(bucket)

    async def request(self, method: str, **kwargs: Any) -> None | dict[Any, Any] | str:
        """Makes the request with ratelimit handling.

        Parameters
        ----------
        method: :class:`str`
            The method to make the request with, E.g `"GET"`.

        kwargs: Any
            The options to pass when requesting, E.g `json=payload`.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong while making the request.

        Returns
        -------
        Union[:class:`dict`, :class:`str`]:
            The return of the request.
        """
        semaphore = await self.ensure()
        route = self.route

        assert self.loop is not None
        async with self.rest.semaphores["global"]:
            await semaphore.acquire()
            await route.event.wait()

            headers = {"Authorization": f"Bot {self.rest.token}"}

            if reason := kwargs.get("reason"):
                headers["X-Audit-Log-Reason"] = reason

            if form := kwargs.pop("form", []):
                formdata = aiohttp.FormData()
                payload = kwargs.pop("json", None)

                if payload:
                    formdata.add_field("payload_json", value=json.dumps(payload))

                for params in form:
                    formdata.add_field(**params)

                kwargs["data"] = formdata

            resp = await self.rest._request(method, self.endpoint, **kwargs)
            data: dict[Any, Any] | str = await resp.data()

            if resp.is_depleted:
                _log.debug(f"BUCKET DEPLETED: {self.bucket} RETRY: {resp.reset_after}s")
                route.event.clear()

                self.loop.call_later(resp.reset_after, route.event.set)
                self.loop.call_later(resp.reset_after, semaphore.release)

                await asyncio.sleep(resp.reset_after)
                return await self.request(method, **kwargs)

            if resp.ok:
                _log.debug(
                    f"{resp.status}: {method} ROUTE: {self.endpoint} REMAINING: {resp.uses}"
                )

                route.event.set()
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
    """A subclass of :class:`aiohttp.ClientResponse`"""

    REMAINING: ClassVar[istr] = istr("X-Ratelimit-Remaining")
    RESET_AT: ClassVar[istr] = istr("X-Ratelimit-Reset-After")
    TOTAL: ClassVar[istr] = istr("X-Ratelimit-Limit")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def data(self) -> Any:
        try:
            return await self.json()
        except aiohttp.ContentTypeError:
            return await self.text()

    @property
    def uses(self) -> int:
        """Uses left in the bucket before it's depleted."""
        return int(self.headers.get(RatelimitedClientResponse.REMAINING, 1))

    @property
    def limit(self) -> int:
        """The total amount of requests of the bucket."""
        return int(self.headers.get(RatelimitedClientResponse.TOTAL, 1))

    @property
    def reset_after(self) -> float:
        """How long until the ratelimit of a bucket resets."""
        return float(self.headers.get(RatelimitedClientResponse.RESET_AT, 0))

    async def retry_after(self) -> None | float:
        """The time to wait before making another request."""
        return (await self.json())["retry_after"] if self.is_ratelimited else None

    @property
    def is_depleted(self) -> bool:
        """If the bucket is currently depleted."""
        return self.status != 429 and self.uses == 0

    @property
    def is_ratelimited(self) -> bool:
        """If the REST API returned a status code `429`."""
        return bool(self.status == 429)
