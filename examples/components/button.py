import asyncio
import os

import rin

client = rin.GatewayClient(
    os.environ["DISCORD_TOKEN"], intents=rin.IntentsBuilder.default()
)


@client.on(rin.Events.READY)
async def ready(user: rin.User) -> None:
    print(f"LOGGED IN AS [{user.snowflake}]")


@client.on(rin.Events.MESSAGE_CREATE)
async def on_message(message: rin.Message) -> None:
    if client.user is not None and client.user.snowflake == message.user.snowflake:
        return

    if message.content.startswith("colour"):
        buttons = rin.ActionRow()

        @rin.button("red", rin.ButtonStyle.DANGER)
        async def red(interaction: rin.Interaction, _: rin.Button) -> None:

            with rin.ANSIBuilder() as ansi:
                ansi(message.content[7:], fore=rin.Color.RED)

                await interaction.send(ansi.final)

        @rin.button("green", rin.ButtonStyle.SUCCESS)
        async def green(interaction: rin.Interaction, _: rin.Button) -> None:

            with rin.ANSIBuilder() as ansi:
                ansi(message.content[7:], fore=rin.Color.GREEN)

                await interaction.send(ansi.final)

        @rin.button("blue", rin.ButtonStyle.PRIMARY)
        async def blue(interaction: rin.Interaction, _: rin.Button) -> None:

            with rin.ANSIBuilder() as ansi:
                ansi(message.content[7:], fore=rin.Color.BLUE)

                await interaction.send(ansi.final)

        buttons.add(red, green, blue)
        await message.reply("Choose an option to colour with.", rows=[buttons])


asyncio.run(client.start())
