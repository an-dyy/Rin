from __future__ import annotations

import asyncio
import os
from typing import Any

import rin


async def main() -> None:
    # pyright: reportUnusedFunction=false
    token: str = os.getenv("DISCORD_TOKEN")  # type: ignore
    client = rin.GatewayClient(token, intents=32509)

    @client.once(rin.Event.READY)
    async def on_ready(user: rin.User) -> None:
        print(f"Logged in as: {user.id}")

    @client.on(rin.Event.MESSAGE_CREATE)
    async def on_message(data: dict[Any, Any]) -> None:
        print(data)

    await client.start()


asyncio.run(main())
