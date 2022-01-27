from __future__ import annotations

import asyncio
import os

import rin


async def main() -> None:
    token: str = os.environ["DISCORD_TOKEN"]
    client = rin.GatewayClient(token, intents=rin.Intents.default())

    @client.once(rin.Events.READY)
    async def ready(user: rin.User) -> None:
        print(f"Logged in as: {user.id}")

    @client.on(rin.Events.MESSAGE_CREATE)
    async def message_created(message: rin.Message) -> None:
        print(f"Received a message! {message}")

    await client.start()


asyncio.run(main())
