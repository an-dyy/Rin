from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import rin

logging.basicConfig(level=logging.DEBUG)


class _CUSTOM_MESSAGE_CREATE(rin.Event[Any]):
    def __init__(self) -> None:
        super().__init__(name="CUSTOM_MESSAGE_CREATE")


CUSTOM_MESSAGE_CREATE = _CUSTOM_MESSAGE_CREATE()


class CustomMessage(rin.Message):
    def __init__(self, client: rin.GatewayClient, data: dict[Any, Any]) -> None:
        super().__init__(client, data)

    @property
    def custom(self) -> str:
        return "Some custom property!"


class GatewayClient(rin.GatewayClient):
    def __init__(self, token: str) -> None:
        intents = rin.Intents.default()
        super().__init__(token, intents=intents)

    @rin.Events.READY.once()
    async def ready(self, user: rin.User) -> None:
        print(f"[LOGGED IN AS]: {user.id}")

    @rin.Events.WILDCARD.on()
    async def websocket_message(
        self, event: rin.Event[Any], data: dict[Any, Any]
    ) -> None:
        if event is not rin.Events.MESSAGE_CREATE:
            return

        self.dispatch(CUSTOM_MESSAGE_CREATE, CustomMessage(self, data))

    @CUSTOM_MESSAGE_CREATE.on()
    async def on_message(self, message: CustomMessage) -> None:
        print(message.custom)


client = GatewayClient(os.environ["DISCORD_TOKEN"])
asyncio.run(client.start())
