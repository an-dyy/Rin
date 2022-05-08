from __future__ import annotations

import asyncio
import os

import rin

token: str = os.environ["DISCORD_TOKEN"]
client = rin.GatewayClient(token, intents=rin.IntentsBuilder.default())


@client.once(rin.Events.READY)
async def ready(user: rin.User) -> None:
    print(f"Logged in as: {user.snowflake}")


@client.on(rin.Events.MESSAGE_CREATE)
async def message_created(message: rin.Message) -> None:
    await message.reply(f"Received your message! {message.content}")


asyncio.run(client.start())
