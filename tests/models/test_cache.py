from __future__ import annotations

import rin


class FakeMessage(rin.Cacheable, max=5):
    def __init__(self, id: int) -> None:
        self.id = id


class TestCache:
    def test_attributes(self) -> None:
        assert hasattr(FakeMessage, "cache")
        assert hasattr(FakeMessage, "__cache__")

        assert not hasattr(FakeMessage(1), "cache")
        assert hasattr(FakeMessage(1), "__cache__")

        assert isinstance(FakeMessage.cache, rin.Cache)

    def test_cache_max(self) -> None:
        assert FakeMessage.cache.max == 5

        for i in range(6):
            FakeMessage.cache.set(i, FakeMessage(i))

        assert FakeMessage.cache.len == 5

    def test_cache_set(self) -> None:
        to_cache = FakeMessage(7)
        FakeMessage.cache.set(7, to_cache)

        assert FakeMessage.cache.len, 5
        assert FakeMessage.cache.get(7) is to_cache

    def test_cache_get(self) -> None:
        for i in range(6):
            FakeMessage.cache.set(i, FakeMessage(i))

        cached = FakeMessage.cache.get(1)

        assert cached is not None
        assert cached.id == 1
