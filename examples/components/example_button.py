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

        @builder.button("Button 1", rin.ButtonStyle.PRIMARY)
        async def button(interaction: rin.Interaction, button: rin.Button) -> None:
            await interaction.send("You pressed button 1!")

        @builder.button("Button 2", rin.ButtonStyle.DANGER)
        async def button2(interaction: rin.Interaction, button: rin.Button) -> None:
            await interaction.send("You pressed button 2, shh...", ephemeral=True)

    if message.content == "Show":
        await message.channel.send("Demo!", rows=[builder])


asyncio.run(client.start())
