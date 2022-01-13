from __future__ import annotations

import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any, Awaitable, Callable

import aiohttp

from .code import OPCode
from .ratelimiter import Ratelimiter

if TYPE_CHECKING:
    from rin.types import DispatchData, HeartbeatData, IdentifyData, ResumeData

    from ..client import GatewayClient

    PayloadData = IdentifyData | DispatchData | ResumeData | HeartbeatData

_log = logging.getLogger(__name__)


class Gateway(aiohttp.ClientWebSocketResponse):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.ratelimiter = Ratelimiter(2, 1)
        self.intents: int
        self.client: GatewayClient

        self.interval: float = 0
        self.pacemaker: asyncio.Task[None]

        self.session_id = ""
        self.sequence = 0

        self.callbacks: dict[int, Callable[..., Awaitable[Any]]] = {
            int(OPCode.DISPATCH): self.send_dispatch,
            int(OPCode.RESUME): self.send_resume,
            int(OPCode.RECONNECT): self.reconnect,
        }

    async def send_dispatch(self, data: dict[Any, Any]) -> None:
        name = data["t"]
        _log.debug(f"GATEWAY SENT: {name}")

        if name == "READY":
            self.session_id = data["d"]["session_id"]

        self.client.dispatcher(name.lower(), data["d"])

    async def send_resume(self, _: dict[Any, Any]) -> None:
        return await self.send(self.resume)

    async def reconnect(self, _: dict[Any, Any]) -> None:
        if not self._closed:
            await self.close()

        _log.debug(
            "GATEWAY SENT RECONNECT: CLOSING WEBSOCKET"
        )  # TODO: Actually restart

    async def start(self, client: GatewayClient) -> None:
        _log.debug("CREATING GATEWAY FROM CLIENT.")

        self.client = client
        self.intents = client.intents

        data = await self.receive_json()
        self.interval = data["d"]["heartbeat_interval"]
        self.pacemaker = self._loop.create_task(self.pulse())

        await self.send(self.identify)
        await self.read_messages()

    async def close(
        self, *, code: int = aiohttp.WSCloseCode.OK, message: bytes = b""
    ) -> bool:
        if self.pacemaker is not None and not self.pacemaker.cancelled():
            self.pacemaker.cancel()

        return await super().close(code=code, message=message)

    async def send(self, payload: PayloadData) -> None:
        await self.ratelimiter.sleep(self.send_json(payload))
        _log.debug(f"SENT GATEWAY: {payload}")

    async def pulse(self) -> None:
        while self.interval is not None and not self._closed:
            await self.send(self.heartbeat)
            self.sequence += 1

            await asyncio.sleep(self.interval / 1000)

    async def read_messages(self) -> None:
        async for message in self:
            if message.type is aiohttp.WSMsgType.TEXT:
                received = message.json()

                if sequence := received.get("s"):
                    self.sequence = sequence

                if callback := self.callbacks.get(received["op"]):
                    await callback(received)

                elif received["op"] == OPCode.HEARTBEAT_ACK:
                    _log.debug("GATEWAY ACK: HEARTBEAT")

        _log.debug(f"WEBSOCKET CLOSED WITH CODE: {self.close_code}")

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
