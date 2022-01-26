from __future__ import annotations

import unittest

import attr
import rin


class TestCache(unittest.TestCase):
    # pyright: reportUnnecessaryIsInstance=false
    """Test :class:`.Base`"""

    def setUp(self) -> None:
        self.client = rin.GatewayClient("TOKEN")

    def test_attributes(self) -> None:
        @attr.s()
        class TestBase(rin.Base):
            id: int = rin.Base.field(cls=int)
            username: str = rin.Base.field()
            optional: None = rin.Base.field()

        test = TestBase(
            self.client, {"id": "123", "username": "test", "optional": None}
        )

        self.assertIsInstance(test.id, int)
        self.assertIsInstance(test.username, str)
        self.assertIsNone(test.optional)

        self.assertEqual(test.id, 123)
        self.assertEqual(test.username, "test")

    def test_aliases(self) -> None:
        @attr.s()
        class TestBase(rin.Base):
            alias: str = rin.Base.field(key="something")

        test = TestBase(self.client, {"something": "something else"})

        self.assertIsInstance(test.alias, str)
        self.assertEqual(test.alias, "something else")

    def test_default(self) -> None:
        @attr.s()
        class TestBase(rin.Base):
            none: None = rin.Base.field()
            defaulted: int = rin.Base.field(default=0)

        test = TestBase(self.client, {})

        self.assertIsNone(test.none)
        self.assertIsInstance(test.defaulted, int)
        self.assertEqual(test.defaulted, 0)

    def test_has_client(self) -> None:
        class Item:
            def __init__(self, client: rin.GatewayClient, username: str) -> None:
                self.username = username
                self.client = client

        @attr.s()
        class TestBase(rin.Base):
            item: Item = rin.Base.field(cls=Item, has_client=True)

        test = TestBase(self.client, {"item": "test"})

        self.assertIsInstance(test.item, Item)
        self.assertTrue(hasattr(test.item, "client"))

    def test_lists(self) -> None:
        class Item:
            def __init__(self, username: str) -> None:
                self.username = username

        @attr.s()
        class TestBase(rin.Base):
            items: list[Item] = rin.Base.field(cls=Item)

        test = TestBase(self.client, {"items": ["1", "2", "3"]})

        self.assertIsInstance(test.items, list)
        self.assertTrue(all([isinstance(item, Item) for item in test.items]))

    def test_cacheable(self) -> None:
        @attr.s()
        class TestBase(rin.Base, rin.Cacheable):
            id: int = rin.Base.field(cls=int)

        test = TestBase(self.client, {"id": "123"})

        self.assertTrue(hasattr(TestBase, "cache"))
        self.assertIsNotNone(TestBase.cache.get(123))
        self.assertIs(TestBase.cache.get(123), test)
        self.assertIsInstance(TestBase.cache.get(123), TestBase)
