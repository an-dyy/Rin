from __future__ import annotations

from typing import Any

import asyncio
import os

import rin


class GatewayClient(rin.GatewayClient):
    def __init__(self, token: str) -> None:
        intents = rin.Intents.default()
        super().__init__(token, intents=intents)

    @rin.Events.READY.once()
    async def ready(self, user: rin.User) -> None:
        print(f"[LOGGED IN AS]: {user.id}")

    @rin.Events.MESSAGE_CREATE.on()
    async def on_message(self, message: dict[Any, Any]) -> None:
        print(f"Received a message! {message}")


client = GatewayClient(os.environ["DISCORD_TOKEN"])
asyncio.run(client.start())
