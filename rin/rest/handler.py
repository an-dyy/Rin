from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp

from .errors import BadRequest, Forbidden, NotFound, Unauthorized

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
    __slots__ = ("session", "token", "client")

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

    async def _create_session(self, cls: type[Gateway] | None) -> aiohttp.ClientSession:
        if cls is not None:
            return aiohttp.ClientSession(
                ws_response_class=cls,
                loop=self.client.loop,
            )

        return aiohttp.ClientSession(loop=self.client.loop)

    async def connect(self, url: str) -> Gateway:
        if not hasattr(self, "session"):
            self.session = await self._create_session(None)

        return await self.session.ws_connect(url)  # type: ignore

    async def request(self, method: str, route: Route, **kwargs: Any) -> Any:
        if not hasattr(self, "session"):
            cls = kwargs.pop("cls") if kwargs.get("cls") else None
            self.session = await self._create_session(cls)

            return await (
                await self.session.request(
                    method,
                    route.endpoint,
                    headers={"Authorization": f"Bot {self.token}"},
                    **kwargs,
                )
            ).json()
