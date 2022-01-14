from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from typing_extensions import Self

__all__ = ("Cache", "Cacheable")

T = TypeVar("T")
CacheableT = TypeVar("CacheableT", bound="Cacheable")


class Cache(Generic[T]):
    def __init__(self, max: None | int = None) -> None:
        self.root: dict[str | int, T] = {}
        self.max = max
        self.len = 0

    def __repr__(self) -> str:
        return f"<Cache max={self.max} len={self.len}>"

    def __setitem__(self, key: str | int, value: T) -> T:
        self.root[key] = value
        self.len += 1

        if self.max and self.len > self.max:
            self.pop()

        return value

    def set(self, key: str | int, value: T) -> T:
        return self.__setitem__(key, value)

    def get(self, key: str | int) -> None | T:
        return self.root.get(key)

    def pop(self, key: None | str | int = None) -> T:
        if key is not None:
            return self.root.pop(key)

        return self.root.pop(list(self.root.keys())[0])


class CacheableMeta(type):
    __cache__: Cache[Any]

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[Any, Any],
        max: None | int = None,
    ) -> CacheableMeta:
        attrs["__cache__"] = Cache[Any](max)
        return super().__new__(cls, name, bases, attrs)

    @property
    def cache(self) -> Cache[Any]:
        return self.__cache__


class Cacheable(metaclass=CacheableMeta):  # Thanks stocker
    __cache__: Cache[Self]  # type: ignore[valid-type]

    if TYPE_CHECKING:

        @classmethod
        @property
        def cache(cls: type[CacheableT]) -> Cache[CacheableT]:
            ...
