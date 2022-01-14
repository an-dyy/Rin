from __future__ import annotations

from typing import Any


class Cache:
    def __init__(self, max: None | int = None, type: None | type[Any] = None) -> None:
        self.root: dict[str | int, Any] = {}
        self.type = type
        self.max = max
        self.len = 0
        self.type = type

    def __repr__(self) -> str:
        return f"<Cache max={self.max} len={self.len}>"

    def __setitem__(self, key: str | int, value: Any) -> None:
        if self.type is not None and not isinstance(value, self.type):
            raise TypeError(
                f"Cannot set value to type of {value!r} when cache type is {self.type!r}"
            ) from None

        self.root[key] = value
        self.len += 1

        if self.max and self.len > self.max:
            self.pop()

    def set(self, key: str | int, value: Any) -> None:
        self.__setitem__(key, value)

    def get(self, key: str | int) -> None | Any:
        return self.root.get(key)

    def pop(self, key: None | str | int = None) -> Any:
        if key is not None:
            return self.root.pop(key)

        return self.root.pop(list(self.root.keys())[0])


class CacheableMeta(type):
    __cache__: Cache

    def __new__(
        cls: type[CacheableMeta],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[Any, Any],
        type: None | type = None,
        max: None | int = None,
    ) -> CacheableMeta:
        attrs["__cache__"] = Cache(max, type=type)
        return super().__new__(cls, name, bases, attrs)

    @property
    def cache(self) -> Cache:
        return self.__cache__


class Cacheable(metaclass=CacheableMeta):
    cache: Cache
