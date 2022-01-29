from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import rin

logging.basicConfig(level=logging.DEBUG)
CUSTOM_MESSAGE_CREATE = rin.Event[Any]("CUSTOM_MESSAGE_CREATE")


class CustomMessage(rin.Message):
    @property
    def custom(self) -> str:
        return "Some custom property!"


client = rin.GatewayClient(os.environ["DISCORD_TOKEN"])


@client.on(rin.Events.WILDCARD)
async def websocket_message(event: rin.Event[Any], data: dict[Any, Any]) -> None:
    if event is not rin.Events.MESSAGE_CREATE:
        return

    client.dispatch(CUSTOM_MESSAGE_CREATE, CustomMessage(client, data))


@client.on(CUSTOM_MESSAGE_CREATE)
async def on_custom(message: CustomMessage) -> None:
    print(message.custom)


asyncio.run(client.start())
