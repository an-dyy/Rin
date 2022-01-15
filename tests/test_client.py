import pytest

import rin


@pytest.mark.asyncio
async def test_on() -> None:
    client = rin.GatewayClient("DISCORD_TOKEN")

    @client.on(rin.Event.MESSAGE_CREATE)
    async def message_create(_) -> None:
        ...

    @client.once(rin.Event.READY)
    async def ready(_) -> None:
        ...

    assert len(client.dispatch.listeners["message_create"]) == 1
    assert len(client.dispatch.once["ready"]) == 1

    await client.dispatch("message_create", {})
    await client.dispatch("ready", {"user": {"id": 1}})

    assert len(client.dispatch.listeners["message_create"]) == 1
    assert len(client.dispatch.once["ready"]) == 0