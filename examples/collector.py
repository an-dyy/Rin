from __future__ import annotations

import asyncio
import os
from datetime import timedelta

import rin

token: str = os.environ["DISCORD_TOKEN"]
intents = rin.IntentsBuilder.default(guild_members=True)
client = rin.GatewayClient(token, intents=intents)


@client.once(rin.Events.READY)
async def ready(user: rin.User) -> None:
    print(f"Logged in as: {user.snowflake}")


@client.collect(rin.Events.GUILD_MEMBER_ADD, timeout=timedelta(seconds=1), amount=5)
async def anti_raid(members: list[rin.Member]) -> None:
    print("Woah! 5 members joined all in 1 second.")
    print("Preparing to ban them just incase of something fishy.")

    asyncio.gather(*(member.ban() for member in members))


asyncio.run(client.start())
