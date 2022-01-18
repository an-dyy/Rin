from __future__ import annotations

import unittest
import rin


class FakeMessage(rin.Cacheable, max=5):
    def __init__(self, id: int) -> None:
        self.id = id


class TestCache(unittest.TestCase):
    """Test :class:`.Cache` and :class:`.Cacheable`"""

    def test_cache(self) -> None:
        self.assertTrue(hasattr(FakeMessage, "cache"))
        self.assertFalse(hasattr(FakeMessage(1), "cache"))
        self.assertIsInstance(FakeMessage.cache, rin.Cache)

    def test_cache_max(self) -> None:
        self.assertEqual(FakeMessage.cache.max, 5)

        for i in range(6):
            FakeMessage.cache.set(i, FakeMessage(i))

        self.assertEqual(FakeMessage.cache.len, 5)

    def test_cache_set(self) -> None:
        to_cache = FakeMessage(7)
        FakeMessage.cache.set(7, to_cache)

        self.assertEqual(FakeMessage.cache.len, 5)
        self.assertIs(FakeMessage.cache.get(7), to_cache)

    def test_cache_get(self) -> None:
        for i in range(6):
            FakeMessage.cache.set(i, FakeMessage(i))

        cached = FakeMessage.cache.get(1)

        self.assertIsNotNone(cached)
        self.assertIs(cached.id, 1)  # type: ignore
