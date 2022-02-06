from __future__ import annotations

import attr
import pytest
import rin


class TestBase:
    @pytest.fixture()
    def client(self) -> rin.GatewayClient:
        return rin.GatewayClient("DISCORD_TOKEN")

    def test_attributes(self, client: rin.GatewayClient) -> None:
        @attr.s()
        class TestBase(rin.Base):
            id: int = rin.Base.field(cls=int)
            username: str = rin.Base.field()
            optional: None = rin.Base.field()

        test = TestBase(
            client,
            {"id": "123", "username": "test", "optional": None},
        )

        assert isinstance(test.id, int)
        assert isinstance(test.username, str)
        assert test.optional is None

        assert test.id == 123
        assert test.username == "test"

    def test_aliases(self, client: rin.GatewayClient) -> None:
        @attr.s()
        class TestBase(rin.Base):
            alias: str = rin.Base.field(key="foo")

        test = TestBase(client, data={"foo": "bar"})
        assert test.alias is not None and test.alias == "bar"

    def test_default(self, client: rin.GatewayClient) -> None:
        @attr.s()
        class TestBase(rin.Base):
            none: None = rin.Base.field()
            defaulted: int = rin.Base.field(default=0)

        test = TestBase(client, {})
        assert test.none is None
        assert test.defaulted is not None and test.defaulted == 0

    def test_has_client(self, client: rin.GatewayClient) -> None:
        class Item:
            def __init__(self, client: rin.GatewayClient, username: str) -> None:
                self.username = username
                self.client = client

        @attr.s()
        class TestBase(rin.Base):
            item: Item = rin.Base.field(cls=Item, has_client=True)

        test = TestBase(client, {"item": "test"})
        assert test.item is not None and isinstance(test.item, Item)
        assert test.client is not None and isinstance(test.client, rin.GatewayClient)

    def test_lists(self, client: rin.GatewayClient) -> None:
        class Item:
            def __init__(self, username: str) -> None:
                self.username = username

        @attr.s()
        class TestBase(rin.Base):
            items: list[Item] = rin.Base.field(cls=Item)

        test = TestBase(client, {"items": ["1", "2", "3"]})

        assert isinstance(test.items, list)
        assert all([isinstance(item, Item) for item in test.items])

    def test_cacheable(self, client: rin.GatewayClient) -> None:
        @attr.s()
        class TestBase(rin.Base, rin.Cacheable):
            id: int = rin.Base.field(cls=int)

        test = TestBase(client, {"id": "123"})

        assert hasattr(TestBase, "cache")
        assert TestBase.cache.get(123) is not None
        assert TestBase.cache.get(123) is test
        assert isinstance(TestBase.cache.get(123), TestBase)
