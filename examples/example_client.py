from __future__ import annotations

from typing import Any

import asyncio
import os

import rin


async def main() -> None:
    # pyright: reportUnusedFunction=false
    client = rin.GatewayClient(
        os.environ["DISCORD_TOKEN"], intents=rin.Intents.default()
    )

    @client.once(rin.Events.READY)
    async def ready(user: rin.User) -> None:
        print(f"Logged in as: {user.id}")

    @client.on(rin.Events.MESSAGE_CREATE)
    async def message_created(message: dict[Any, Any]) -> None:
        print(f"Received a message! {message}")

    await client.start()


asyncio.run(main())
