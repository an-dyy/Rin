from __future__ import annotations

import asyncio
import logging
import sys
import typing

import aiohttp

from .code import OPCode
from .ratelimiter import Ratelimiter

if typing.TYPE_CHECKING:
    from ..client import GatewayClient
    from ..types import DispatchData, HeartbeatData, IdentifyData, ResumeData

_log = logging.getLogger(__name__)


class Gateway:
    __slots__ = (
        "limiter",
        "client",
        "intents",
        "sock",
        "session_id",
        "sequence",
        "loop",
        "show_payload",
    )

    def __init__(
        self,
        client: GatewayClient,
        sock: aiohttp.ClientWebSocketResponse,
        *,
        show_payload: bool = False,
    ) -> None:
        self.show_payload = show_payload
        self.limiter = Ratelimiter(2, 1)
        self.intents = client.intents
        self.loop = client.loop
        self.client = client
        self.sock = sock

        self.session_id = ""
        self.sequence = 0

    @classmethod
    async def from_url(
        cls: type[Gateway],
        client: GatewayClient,
        url: str,
        *,
        show_payload: bool = False,
    ) -> Gateway:
        sock = await client.rest.connect(url)
        return cls(client, sock, show_payload=show_payload)

    def dispatch(self, name: str, data: dict[typing.Any, typing.Any]) -> None:
        _log.debug(f"GATEWAY SENT: {name} {data if self.show_payload else ''}")

        if name == "READY":
            self.session_id = data["session_id"]

        self.client.dispatcher(name.lower(), data)

    async def send(
        self, data: DispatchData | IdentifyData | ResumeData | HeartbeatData
    ) -> None:
        _log.debug(f"SENDING GATEWAY: {data if self.show_payload else data['op']}")
        await self.limiter.sleep(self.sock.send_json(data))

    async def pulse(self, interval: float) -> None:
        while not self.sock.closed:
            await self.send(self.heartbeat)
            self.sequence += 1

            await asyncio.sleep(interval / 1000)

    async def read(self) -> None:
        async for message in self.sock:
            if message.type is aiohttp.WSMsgType.TEXT:
                data = message.json()

                if data["op"] == OPCode.HELLO:
                    self.loop.create_task(self.pulse(data["d"]["heartbeat_interval"]))
                    await self.send(self.identify)

                elif data["op"] == OPCode.DISPATCH:
                    self.dispatch(data["t"], data["d"])

                elif data["op"] == OPCode.RESUME:
                    await self.send(self.resume)

                elif data["op"] == OPCode.RECONNECT:
                    if not self.sock.closed:
                        await self.sock.close()

                    await self.read()

                elif data["op"] == OPCode.HEARTBEAT_ACK:
                    _log.debug("GATEWAY ACK: HEARTBEAT")

        _log.debug(self.sock.close_code)

    @property
    def identify(self) -> IdentifyData:
        return {
            "op": int(OPCode.IDENTIFY),
            "d": {
                "token": self.client.rest.token,
                "intents": self.intents,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "Rin 0.1.0-alpha",
                    "$device": "Rin 0.1.0-alpha",
                },
            },
        }

    @property
    def resume(self) -> ResumeData:
        return {
            "op": int(OPCode.RESUME),
            "d": {
                "token": self.client.rest.token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        }

    @property
    def heartbeat(self) -> HeartbeatData:
        return {"op": int(OPCode.HEARTBEAT), "d": self.sequence}
