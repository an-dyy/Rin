from __future__ import annotations

import asyncio

import pytest

import rin

# pyright: reportUnusedFunction=false


@pytest.mark.asyncio
async def test_client_on() -> None:
    client = rin.GatewayClient("DISCORD_TOKEN")

    @client.on(rin.Event.MESSAGE_CREATE)
    async def test_message_create(data: dict[str, bool]) -> None:
        assert data["test"] is True

    assert len(client.dispatch.listeners[rin.Event.MESSAGE_CREATE]) == 1
    tasks = client.dispatch(rin.Event.MESSAGE_CREATE, {"test": True})

    for task in tasks:
        await task


@pytest.mark.asyncio
async def test_client_once() -> None:
    client = rin.GatewayClient("DISCORD_TOKEN")

    @client.once(rin.Event.READY)
    async def test_ready(user: dict[str, int]) -> None:
        assert user["id"] == 1

    assert len(client.dispatch.once[rin.Event.READY]) == 1
    tasks = client.dispatch(rin.Event.READY, {"id": 1})

    assert len(client.dispatch.once[rin.Event.READY]) == 0
    tasks.extend(client.dispatch(rin.Event.READY, {"id": 2}))

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

    collector = client.dispatch.collectors[rin.Event.MESSAGE_CREATE]

    assert collector.callback is test_message_create_collect
    assert collector.check.__name__ == "<lambda>"
    assert collector.queue.maxsize == 5

    for i in range(5):
        task = await collector.dispatch(asyncio.get_running_loop(), {"id": i})

        if task is not None:
            await task
