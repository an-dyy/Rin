from __future__ import annotations

from typing_extensions import Self

import rin


class FakeMessage(rin.Cacheable, max=5):
    cache: rin.Cache[Self]  # type: ignore[valid-type]

    def __init__(self, id: int) -> None:
        self.id = id


def test_cache_max() -> None:
    for i in range(6):
        FakeMessage.cache.set(i, FakeMessage(i))

    assert len(FakeMessage.cache.root.keys()) == 5


def test_cache_get() -> None:
    assert (
        isinstance(message := FakeMessage.cache.get(1), FakeMessage)
        and message is not None
    )
    assert message.id == 1
