import pytest

import rin


@pytest.mark.asyncio
async def test_on() -> None:
    client = rin.GatewayClient("DISCORD_TOKEN")

    @client.on(rin.Event.MESSAGE_CREATE)
    async def message_create(_: dict[str, str]) -> None:
        ...

    @client.once(rin.Event.READY)
    async def ready(_: dict[str, str]) -> None:
        ...

    assert len(client.dispatch.listeners["message_create"]) == 1
    assert len(client.dispatch.once["ready"]) == 1

    client.dispatch("message_create", {})
    client.dispatch("ready", {"user": {"id": 1}})

    assert len(client.dispatch.listeners["message_create"]) == 1
    assert len(client.dispatch.once["ready"]) == 0
