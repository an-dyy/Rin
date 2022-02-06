from __future__ import annotations

import asyncio
import types
from typing import Any
from unittest import mock

import pytest

import rin


class TestGatewayClient:
    # pyright: reportUnknownMemberType=false

    @pytest.fixture()
    def client(self) -> rin.GatewayClient:
        return rin.GatewayClient("DISCORD_TOKEN")

    def test_attributes(self, client: rin.GatewayClient) -> None:
        assert isinstance(client, rin.GatewayClient)

        assert client.token is not None and isinstance(client.token, str)
        assert client.gateway is not None and isinstance(client.gateway, rin.Gateway)
        assert client.rest is not None and isinstance(client.rest, rin.RESTClient)
        assert client.intents.value == rin.Intents.default().value

        assert client.no_chunk is False
        assert client.closed is False
        assert client.loop is None

        assert not hasattr(client, "user")

    @pytest.mark.asyncio()
    async def test_start(self, client: rin.GatewayClient) -> None:
        client.loop = asyncio.get_running_loop()

        with mock.patch.object(rin.Gateway, "start") as start_mock:
            start_mock: mock.MagicMock

            await client.gateway.start()
            start_mock.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_close(self, client: rin.GatewayClient) -> None:
        client.rest.session = mock.AsyncMock()
        client.rest.session.close = mock.AsyncMock()

        with mock.patch.object(rin.Gateway, "close") as close_mock:
            close_mock: mock.MagicMock

            await client.close()
            client.rest.session.close.assert_awaited_once()
            close_mock.assert_awaited_once()

    def test_unserialize(self, client: rin.GatewayClient) -> None:
        class TestUnserialize:
            def __init__(self, client: rin.GatewayClient, data: dict[Any, Any]) -> None:
                self.client = client
                self.data = data

            @property
            def name(self) -> None | str:
                return self.data.get("name")

        test = client.unserialize({"name": "Foo!"}, cls=TestUnserialize)
        assert test.client is client
        assert test.name == "Foo!"

    def test_dispatch(self, client: rin.GatewayClient) -> None:
        event = mock.MagicMock()
        event.dispatch = mock.MagicMock()

        client.dispatch(event, "foo")
        event.dispatch.assert_called_once()

    def test_collect(self, client: rin.GatewayClient) -> None:
        # pyright: reportUntypedFunctionDecorator=false
        # pyright: reportGeneralTypeIssues=false

        with pytest.raises(TypeError):

            @client.collect(rin.Events.MESSAGE_CREATE)
            async def test_register() -> None:
                ...

            assert isinstance(test_register, types.FunctionType)

        @client.collect(rin.Events.MESSAGE_CREATE, amount=5)
        async def test_collector() -> None:
            ...

        assert isinstance(test_collector, rin.Collector)

    def test_on(self, client: rin.GatewayClient) -> None:
        # pyright: reportUntypedFunctionDecorator=false
        # pyright: reportGeneralTypeIssues=false

        with pytest.raises(TypeError):

            @client.on()
            async def test_register() -> None:
                ...

            assert isinstance(test_register, types.FunctionType)

        @client.on(rin.Events.MESSAGE_CREATE)
        async def test_collector() -> None:
            ...

        assert isinstance(test_collector, rin.Listener)

    def test_once(self, client: rin.GatewayClient) -> None:
        # pyright: reportUntypedFunctionDecorator=false
        # pyright: reportGeneralTypeIssues=false

        with pytest.raises(TypeError):

            @client.once()
            async def test_register() -> None:
                ...

            assert isinstance(test_register, types.FunctionType)

        @client.once(rin.Events.MESSAGE_CREATE)
        async def test_collector() -> None:
            ...

        assert isinstance(test_collector, rin.Listener)
        assert test_collector.once is True
