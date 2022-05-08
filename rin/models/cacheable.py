from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterator, TypeVar

import attr

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ("Cache", "Cacheable")
T = TypeVar("T")


@attr.s(slots=True)
class Cache(Generic[T]):
    """A class which represents an in-memory cache.

    .. note::
        All cache-able classes have this class under the attribute `Class.cache`

    .. code:: python

        user: rin.User = rin.User.cache.get(123)
        rin.User.cache.set(123, User)

    Parameters
    ----------
    max: None | :class:`int`
        The max amount of items before poping the last
        inserted object.

    Attributes
    ----------
    root: :class:`dict`
        The internal dict of the cache.

    max: None | :class:`int`
        The max amount of items the cache can have
        at a given time.

    len: :class:`int`
        The current amount of items in the cache.
    """

    max: None | int = attr.field()
    len: int = attr.field(default=0)

    root: dict[str | int, T] = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.root: dict[str | int, T] = {}

    def __setitem__(self, key: str | int, value: T) -> T:
        self.root[key] = value
        self.len += 1

        if self.max and self.len > self.max:
            self.len -= 1
            self.pop()

        return value

    def __getitem__(self, key: str | int) -> T:
        return self.root[key]

    def iterator(self) -> Iterator[T]:
        """An iterator for the cache's values.

        Returns
        -------
        :class:`typing.Iterator[T]`
            An iterator of the values.
        """
        yield from self.root.values()

    def set(self, key: str | int, value: T) -> T:
        """Sets a key to the given value.

        Parameters
        ----------
        key: :class:`str` | :class:`int`
            The key to set.

        value: :class:`typing.Any`
            The value to set to the key.

        Returns
        -------
        :class:`typing.Any`:
            The value being set.
        """
        return self.__setitem__(key, value)

    def get(self, key: str | int) -> None | T:
        """Retrieves a value from the given key.

        Parameters
        ----------
        key: :class:`str` | :class:`int`
            The key to retrieve from.

        Returns
        -------
        None | :class:`typing.Any`
            The value retrieved from the key.
        """
        return self.root.get(key)

    def pop(self, key: None | str | int = None) -> T:
        """Pops an item from the internal dict.

        If no key is passed, the last inserted key will be popped.

        Parameters
        ----------
        key: None | :class:`str` | :class:`int`
            The key to pop from the internal dict.

        Returns
        -------
        :class:`typing.Any`
            The value from the popped key.
        """
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
    """Represents a class that is cache-able.

    Attributes
    ----------
    cache: :class:`.Cache`
        The cache of the class.
    """

    __cache__: Cache[Self]

    if TYPE_CHECKING:

        @classmethod
        @property
        def cache(cls: type[Self]) -> Cache[Self]:
            ...
