from __future__ import annotations

import asyncio
import os
from datetime import timedelta

import rin


async def main() -> None:
    token: str = os.environ["DISCORD_TOKEN"]
    client = rin.GatewayClient(token, intents=rin.Intents.default(guild_members=True))

    @client.once(rin.Events.READY)
    async def ready(user: rin.User) -> None:
        print(f"Logged in as: {user.id}")

    @client.collect(rin.Events.GUILD_MEMBER_ADD, timeout=timedelta(seconds=1), amount=5)
    async def anti_raid(members: list[rin.Member]) -> None:
        print("Woah! 5 members joined all in 1 second.")
        print("Preparing to ban them just incase of something fishy.")

        asyncio.gather(*(member.ban() for member in members))

    await client.start()


asyncio.run(main())
