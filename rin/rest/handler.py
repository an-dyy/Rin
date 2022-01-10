from __future__ import annotations

import typing

import aiohttp

__all__ = ("RESTClient", "Route")


class Route:
    BASE = "https://discord.com/api/v{0}/"

    def __init__(self, endpoint: str, *, version: str = "9") -> None:
        self.endpoint = Route.BASE.format(version) + endpoint


class RESTClient:
    __slots__ = ("session", "token")

    def __init__(self, token: str) -> None:
        self.session: aiohttp.ClientSession
        self.token = token

    async def _create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    async def connect(self, url: str) -> aiohttp.ClientWebSocketResponse:
        if not hasattr(self, "session"):
            self.session = await self._create_session()

        return await self.session.ws_connect(url)

    async def request(
        self, method: str, route: Route, **kwargs: typing.Any
    ) -> typing.Any:
        if not hasattr(self, "session"):
            self.session = await self._create_session()

        resp = await self.session.request(
            method,
            route.endpoint,
            json=kwargs if kwargs else None,
            headers={"Authorization": f"Bot {self.token}"},
        )

        return await resp.json()
