from __future__ import annotations

from typing import Any
import textwrap

import asyncio
import logging
import os

import rin

logging.basicConfig(level=logging.DEBUG)


class _CUSTOM_MESSAGE_CREATE(rin.Event[Any]):
    def __init__(self) -> None:
        super().__init__(name="CUSTOM_MESSAGE_CREATE")


CUSTOM_MESSAGE_CREATE = _CUSTOM_MESSAGE_CREATE()


class CustomMessage:
    def __init__(self, client: rin.GatewayClient, data: dict[Any, Any]) -> None:
        self.client = client
        self.data = data

    @property
    def content(self) -> str:
        return self.data["content"]

    @property
    def channel_id(self) -> int:
        return int(self.data["channel_id"])

    async def eval(self) -> None:
        content = self.content[1:]
        route = rin.Route(
            f"channels/{self.channel_id}/messages", channel_id=self.channel_id
        )

        enviornment: dict[Any, Any] = {
            "rin": rin,
            "GatewayClient": GatewayClient,
            "self": self,
        }

        cleaned = content.strip("```").removeprefix("py")
        final = textwrap.indent(cleaned, prefix="\t")

        exec(f"async def __eval__():\n{final}", enviornment)
        ret = repr(await enviornment["__eval__"]())

        await self.client.rest.request("POST", route, json={"content": ret[:2000]})


class GatewayClient(rin.GatewayClient):
    def __init__(self, token: str) -> None:
        intents = rin.Intents.default()
        super().__init__(token, intents=intents)

    @staticmethod
    def check(event: rin.Event[Any], data: dict[Any, Any]) -> bool:
        return (
            event is rin.Events.MESSAGE_CREATE
            and data["author"]["id"] == "270700034985558017"
        )

    @rin.Events.READY.once()
    async def ready(self, user: rin.User) -> None:
        print(f"[LOGGED IN AS]: {user.id}")

    @rin.Events.WILDCARD.on(check=lambda event, data: GatewayClient.check(event, data))
    async def on_websocket_message(
        self, _: rin.Event[Any], data: dict[Any, Any]
    ) -> None:
        self.dispatch(CUSTOM_MESSAGE_CREATE, CustomMessage(self, data))

    @CUSTOM_MESSAGE_CREATE.on()
    async def on_message(self, message: CustomMessage) -> None:
        if message.content.startswith(";"):
            await message.eval()


client = GatewayClient(os.environ["DISCORD_TOKEN"])
asyncio.run(client.start())
