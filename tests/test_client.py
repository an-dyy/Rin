from __future__ import annotations

import unittest
from asyncio import gather, get_running_loop
from unittest.mock import AsyncMock

import rin


class TestClient(unittest.IsolatedAsyncioTestCase):
    # pyright: reportUnusedFunction=false
    """Test :class:`.GatewayClient`"""

    async def test_on(self) -> None:
        client = rin.GatewayClient("DISCORD_TOKEN")
        client.loop = get_running_loop()

        listeners = client.dispatch.listeners[rin.Event.READY]
        self.assertEqual(len(listeners), 0)

        mock = AsyncMock(__name__="<MOCK>")
        client.subscribe(rin.Event.READY, mock)

        self.assertEqual(len(listeners), 1)
        await gather(*client.dispatch(rin.Event.READY, {}))

        mock.assert_awaited()

    async def test_once(self) -> None:
        client = rin.GatewayClient("DISCORD_TOKEN")
        client.loop = get_running_loop()

        listeners = client.dispatch.once[rin.Event.READY]
        self.assertEqual(len(listeners), 0)

        mock = AsyncMock(__name__="<MOCK>")
        client.subscribe(rin.Event.READY, mock, once=True)

        self.assertEqual(len(listeners), 1)
        await gather(*client.dispatch(rin.Event.READY, {}))
        await gather(*client.dispatch(rin.Event.READY, {}))

        mock.assert_awaited_once()

    async def test_collector(self) -> None:
        client = rin.GatewayClient("DISCORD_TOKEN")
        client.loop = get_running_loop()

        mock = AsyncMock(__name__="<MOCK>")
        client.subscribe(rin.Event.READY, mock, collect=5)

        collector = client.dispatch.collectors.get(rin.Event.READY)

        if collector is not None:
            self.assertIs(collector.callback, mock)
            self.assertEqual(collector.check.__name__, "<lambda>")
            self.assertEqual(collector.queue.maxsize, 5)

        elif collector is None:
            self.assertIsNotNone(collector)

        for _ in range(5):
            await gather(*client.dispatch(rin.Event.READY, get_running_loop(), {}))

        mock.assert_awaited_once()
