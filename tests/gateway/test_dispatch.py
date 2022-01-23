from __future__ import annotations

from typing import Any

import asyncio

import unittest
from unittest import mock

import rin


class TestDispatch(unittest.IsolatedAsyncioTestCase):
    # pyright: reportUnusedFunction=false
    """Testing the dispatch system."""

    async def asyncSetUp(self) -> None:
        self.client = rin.GatewayClient("DISCORD_TOKEN")
        self.client.loop = asyncio.get_running_loop()
        self.dispatch = self.client.dispatch

    async def wait(self, tasks: list[asyncio.Task[Any]]) -> None:
        await asyncio.gather(*tasks)

    async def test_dispatch(self) -> None:
        self.assertTrue(hasattr(self.client, "dispatch"))

        @self.client.on(rin.Event.READY)
        async def test_ready(mock: mock.AsyncMock) -> None:
            await mock()

        self.assertIsInstance(test_ready, rin.Listener)

        test_mock = mock.AsyncMock()
        await self.wait(self.dispatch(rin.Event.READY, test_mock))

        test_mock.assert_awaited()

    async def test_once_dispatch(self) -> None:
        self.assertTrue(hasattr(self.client, "dispatch"))

        @self.client.once(rin.Event.READY)
        async def test_ready(mock: mock.AsyncMock) -> None:
            await mock()

        self.assertIsInstance(test_ready, rin.Listener)

        test_mock = mock.AsyncMock()
        await self.wait(self.dispatch(rin.Event.READY, test_mock))
        await self.wait(self.dispatch(rin.Event.READY, test_mock))

        test_mock.assert_awaited_once()

    async def test_collector_dispatch(self) -> None:
        self.assertTrue(hasattr(self.client, "dispatch"))

        @self.client.collect(rin.Event.READY, amount=5)
        async def test_ready(mocks: list[mock.AsyncMock]) -> None:
            for test_mock in mocks:
                await test_mock()

        self.assertIsInstance(test_ready, rin.Collector)
        test_mocks = [mock.AsyncMock() for _ in range(5)]

        for test_mock in test_mocks:
            await self.wait(self.dispatch(rin.Event.READY, test_mock))

        for test_mock in test_mocks:
            test_mock.assert_awaited()
