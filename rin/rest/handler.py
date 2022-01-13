from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from ..client import GatewayClient
    from ..gateway import Gateway

__all__ = ("RESTClient", "Route")


class Route:
    __slots__ = "endpoint"

    BASE = "https://discord.com/api/v{0}/"

    def __init__(self, endpoint: str, *, version: str = "9") -> None:
        self.endpoint = Route.BASE.format(version) + endpoint


class RESTClient:
    __slots__ = ("session", "token", "client")

    def __init__(self, token: str, client: GatewayClient) -> None:
        self.session: aiohttp.ClientSession
        self.token = token
        self.client = client

    async def _create_session(self, cls: type[Gateway] | None) -> aiohttp.ClientSession:
        if cls is not None:
            return aiohttp.ClientSession(ws_response_class=cls, loop=self.client.loop)

        return aiohttp.ClientSession(loop=self.client.loop)

    async def connect(self, url: str) -> Gateway:
        if not hasattr(self, "session"):
            self.session = await self._create_session(None)

        return await self.session.ws_connect(url)  # type: ignore

    async def request(self, method: str, route: Route, **kwargs: Any) -> Any:
        if not hasattr(self, "session"):
            cls = kwargs.pop("cls") if kwargs.get("cls") else None
            self.session = await self._create_session(cls)

        resp = await self.session.request(
            method,
            route.endpoint,
            json=kwargs if kwargs else None,
            headers={"Authorization": f"Bot {self.token}"},
        )

        return await resp.json()
