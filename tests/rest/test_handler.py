from __future__ import annotations

import asyncio
from unittest import mock

import aiohttp
import pytest

import rin


class TestRESTClient:
    @pytest.fixture()
    def rest(self) -> rin.RESTClient:
        return rin.RESTClient("DISCORD_TOKEN", rin.GatewayClient("DISCORD_TOKEN"))

    def test_attributes(self, rest: rin.RESTClient) -> None:
        assert rest.__class__.ERRORS == {
            400: rin.BadRequest,
            401: rin.Unauthorized,
            403: rin.Forbidden,
            404: rin.NotFound,
        }

        assert rest.token is not None and isinstance(rest.token, str)
        assert rest.client is not None and isinstance(rest.client, rin.GatewayClient)

        assert rest.semaphores.get("global") is not None
        assert isinstance(rest.semaphores["global"], asyncio.Semaphore)
        assert rest.semaphores["global"]._value == 50

        assert not hasattr(rest, "session")

    @pytest.mark.asyncio()
    async def test_create_session(self, rest: rin.RESTClient) -> None:
        rest.client.loop = asyncio.get_running_loop()
        session = await rest._create_session()

        assert session is not None and isinstance(session, aiohttp.ClientSession)

    @pytest.mark.asyncio()
    async def test_connect(self, rest: rin.RESTClient) -> None:
        # pyright: reportUnknownMemberType=false

        rest.session = mock.AsyncMock()
        rest.session.ws_connect = mock.AsyncMock()

        await rest.connect("foo")
        rest.session.ws_connect.assert_awaited_once_with("foo")

    @pytest.mark.asyncio()
    async def test_request(self, rest: rin.RESTClient) -> None:
        rest.client.loop = asyncio.get_running_loop()

        with mock.patch.object(rin.Ratelimiter, "request") as request_mock:
            request_mock: mock.MagicMock

            await rest.request("GET", rin.Route("test"))
            request_mock.assert_awaited()
