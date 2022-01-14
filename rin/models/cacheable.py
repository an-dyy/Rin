from __future__ import annotations

from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Cache(Generic[T]):
    def __init__(self, max: None | int = None) -> None:
        self.root: dict[str | int, T] = {}
        self.max = max
        self.len = 0

    def __repr__(self) -> str:
        return f"<Cache max={self.max} len={self.len}>"

    def __setitem__(self, key: str | int, value: T) -> None:
        self.root[key] = value
        self.len += 1

        if self.max and self.len > self.max:
            self.pop()

    def set(self, key: str | int, value: T) -> None:
        self.__setitem__(key, value)

    def get(self, key: str | int) -> None | T:
        return self.root.get(key)

    def pop(self, key: None | str | int = None) -> T:
        if key is not None:
            return self.root.pop(key)

        return self.root.pop(list(self.root.keys())[0])


class CacheableMeta(type):
    __cache__: Cache[Any]

    def __new__(
        cls: type[CacheableMeta],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[Any, Any],
        type: None | type = None,
        max: None | int = None,
    ) -> CacheableMeta:

        type = type or cls
        attrs["__cache__"] = Cache[type](max)  # type: ignore
        return super().__new__(cls, name, bases, attrs)

    @property
    def cache(self) -> Cache[Any]:
        return self.__cache__


class Cacheable(metaclass=CacheableMeta):
    cache: Cache[Any]
