from __future__ import annotations

from typing import Any

import pytest

import rin


@pytest.mark.asyncio
async def test_client_on() -> None:
    client = rin.GatewayClient("DISCORD_TOKEN")

    @client.on(rin.Event.MESSAGE_CREATE)
    async def test_message_create(data: dict[str, bool]) -> None:
        assert data["test"] is True

    assert len(client.dispatch.listeners["message_create"]) == 1
    tasks = client.dispatch("message_create", {"test": True})

    for task in tasks:
        await task


@pytest.mark.asyncio
async def test_client_once() -> None:
    client = rin.GatewayClient("DISCORD_TOKEN")

    @client.once(rin.Event.READY)
    async def test_ready(user: dict[str, int]) -> None:
        assert user["id"] == 1

    assert len(client.dispatch.once["ready"]) == 1
    tasks = client.dispatch("ready", {"id": 1})

    assert len(client.dispatch.once["ready"]) == 0
    tasks.extend(client.dispatch("ready", {"id": 2}))

    for task in tasks:
        await task


@pytest.mark.asyncio
async def test_client_collect() -> None:
    client = rin.GatewayClient("DISCORD_TOKEN")

    @client.collect(rin.Event.MESSAGE_CREATE, amount=5)
    async def test_message_create_collect(messages: list[dict[str, int]]) -> None:
        assert len(messages) == 5

        for i in range(5):
            assert messages[i]["id"] == i

    queue, callback, check = client.dispatch.collectors["message_create"]

    assert callback is test_message_create_collect
    assert check.__name__ == "<lambda>"
    assert queue.maxsize == 5

    for i in range(5):
        task = await client.dispatch.dispatch_collector(queue, callback, {"id": i})

        if task is not None:
            await task
