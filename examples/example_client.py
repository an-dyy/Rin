from __future__ import annotations

import asyncio
import os

import rin


async def main() -> None:
    # pyright: reportUnusedFunction=false
    token: str = os.getenv("DISCORD_TOKEN")  # type: ignore
    client = rin.GatewayClient(token, intents=rin.Intents.default())

    @client.once(rin.Events.READY)
    async def on_ready(user: rin.User) -> None:
        print(f"Logged in as: {user.id}")

    await client.start()


asyncio.run(main())
