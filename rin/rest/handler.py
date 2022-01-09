from __future__ import annotations

import aiohttp

__all__ = ("RESTClient",)


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
