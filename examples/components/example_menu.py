from __future__ import annotations

import asyncio
import os

import rin

token: str = os.environ["DISCORD_TOKEN"]
client = rin.GatewayClient(token, intents=rin.Intents.default())


@client.once(rin.Events.READY)
async def ready(user: rin.User) -> None:
    print(f"Logged in as: {user.id}")


@client.on(rin.Events.MESSAGE_CREATE)
async def message_created(message: rin.Message) -> None:
    if message.author.bot is True:
        return

    with rin.ActionRowBuilder() as builder:
        with rin.SelectMenuBuilder() as menu:
            menu.option("Option 1", "Value 1")
            menu.option("Option 2", "Value 2")
            menu.option("Option 3", "Value 3")
            menu.option("Option 4", "Value 4")
            menu.option("Option 5", "Value 5")

        @menu.set_callback()
        async def callback(interaction: rin.Interaction, menu: rin.SelectMenu) -> None:
            await interaction.send(f"Woah you selected: {menu.values}")

        builder.add(menu)

    if message.content == "Show":
        await message.channel.send("Demo!", rows=[builder])


asyncio.run(client.start())
