from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, ClassVar, overload

import aiohttp

from .errors import BadRequest, Forbidden, NotFound, Unauthorized
from .ratelimiter import RatelimitedClientResponse, Ratelimiter

if TYPE_CHECKING:
    from ..client import GatewayClient
    from ..gateway import Gateway

__all__ = ("RESTClient", "Route")


class Route:
    __slots__ = (
        "endpoint",
        "lock",
        "channel_id",
        "guild_id",
        "webhook_id",
        "webhook_token",
    )

    BASE = "https://discord.com/api/v{0}/"

    def __init__(self, endpoint: str, *, version: str = "9", **kwargs: Any) -> None:
        self.endpoint = Route.BASE.format(version) + endpoint
        self.lock = asyncio.Lock()

        self.channel_id: None | int = kwargs.get("channel_id")
        self.guild_id: None | int = kwargs.get("guild_id")
        self.webhook_id: None | int = kwargs.get("webhook_id")
        self.webhook_token: None | str = kwargs.get("webhookd_token")

    @property
    def bucket(self) -> str:
        return f"{self.channel_id}/{self.guild_id}/{self.webhook_id}/{self.endpoint}"


class RESTClient:
    __slots__ = ("session", "token", "client", "semaphores")

    GATEWAY_TYPE: ClassVar[type[Gateway]]
    ERRORS: ClassVar[dict[int, Any]] = {
        400: BadRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
    }

    def __init__(self, token: str, client: GatewayClient) -> None:
        self.session: aiohttp.ClientSession
        self.token = token
        self.client = client

        self.semaphores: dict[str, asyncio.Semaphore] = {
            "global": asyncio.Semaphore(50)
        }

    async def _create_session(self) -> aiohttp.ClientSession:
        if hasattr(self, "session"):
            return self.session

        return aiohttp.ClientSession(
            ws_response_class=RESTClient.GATEWAY_TYPE,
            response_class=RatelimitedClientResponse,
            loop=self.client.loop,
        )

    async def connect(self, url: str) -> Gateway:
        if not hasattr(self, "session"):
            self.session = await self._create_session()

        return await self.session.ws_connect(url)  # type: ignore

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> RatelimitedClientResponse:
        self.session = await self._create_session()

        return await self.session.request(  # type: ignore
            method,
            endpoint,
            headers={"Authorization": f"Bot {self.token}"},
            **kwargs,
        )

    async def request(self, method: str, route: Route, **kwargs: Any) -> Any:
        async with Ratelimiter(self, route) as handler:
            return await handler.request(method, **kwargs)
