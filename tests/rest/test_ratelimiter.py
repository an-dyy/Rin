from __future__ import annotations

import asyncio
from unittest import mock

import pytest

import rin


class TestRatelimiter:
    # pyright: reportUnknownMemberType=false

    @pytest.fixture()
    def rest(self) -> rin.RESTClient:
        return rin.RESTClient("DISCORD_TOKEN", rin.GatewayClient("DISCORD_TOKEN"))

    @pytest.fixture()
    def route(self) -> rin.Route:
        return rin.Route("test/ratelimiter")

    @pytest.fixture()
    def ratelimiter(self, rest: rin.RESTClient, route: rin.Route) -> rin.Ratelimiter:
        rest.client.loop = mock.MagicMock()
        return rin.Ratelimiter(rest, route)

    def test_attributes(
        self, ratelimiter: rin.Ratelimiter, rest: rin.RESTClient, route: rin.Route
    ) -> None:
        assert ratelimiter.route is route
        assert ratelimiter.rest is rest
        assert ratelimiter.loop is ratelimiter.rest.client.loop
        assert ratelimiter.auth == {"Authorization": "Bot DISCORD_TOKEN"}
        assert ratelimiter.endpoint == ratelimiter.route.endpoint
        assert ratelimiter.bucket == ratelimiter.route.bucket

    @pytest.mark.asyncio
    async def test_ensure(self, ratelimiter: rin.Ratelimiter) -> None:
        resp_mock = mock.MagicMock()
        resp_mock.limit = 1

        with mock.patch.object(
            rin.RESTClient, "_request", return_value=resp_mock
        ) as request_mock:
            ret = await ratelimiter.ensure()
            request_mock.assert_awaited_once()

        assert ratelimiter.rest.semaphores[ratelimiter.bucket] is ret
        assert ret is not None and isinstance(ret, asyncio.Semaphore)
        assert ret._value == 1

    def test_get(self, ratelimiter: rin.Ratelimiter) -> None:
        assert ratelimiter.get(ratelimiter.bucket) is None
