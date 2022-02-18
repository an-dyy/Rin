from __future__ import annotations

import asyncio
import os
from typing import Any

import rin

CUSTOM_MESSAGE_CREATE = rin.Event[Any]("CUSTOM_MESSAGE_CREATE")
client = rin.GatewayClient(os.environ["DISCORD_TOKEN"])


class CustomMessage(rin.Message):
    @property
    def custom(self) -> str:
        return "Some custom property!"


@client.on(rin.Events.WILDCARD)
async def websocket_message(event: rin.Event[Any], data: dict[Any, Any]) -> None:
    if event is not rin.Events.MESSAGE_CREATE:
        return

    client.dispatch(CUSTOM_MESSAGE_CREATE, CustomMessage(client, data))


@client.on(CUSTOM_MESSAGE_CREATE)
async def on_custom(message: CustomMessage) -> None:
    print(message.custom)


asyncio.run(client.start())
