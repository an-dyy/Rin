from __future__ import annotations

import asyncio
import os

import rin


class GatewayClient(rin.GatewayClient):
    def __init__(self, token: str) -> None:
        intents = rin.IntentsBuilder.default()
        super().__init__(token, intents=intents)

    @rin.Events.READY.once()
    async def ready(self, user: rin.User) -> None:
        print(f"[LOGGED IN AS]: {user.snowflake}")

    @rin.Events.MESSAGE_CREATE.on()
    async def on_message(self, message: rin.Message) -> None:
        await message.reply(f"Received your message! {message.content}")


client = GatewayClient(os.environ["DISCORD_TOKEN"])
asyncio.run(client.start())
