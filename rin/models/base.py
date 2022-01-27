from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable

import attr

from .cacheable import Cacheable

if TYPE_CHECKING:
    from rin import GatewayClient

__all__ = ("Base",)


@attr.s()
class Base:
    """A base class used in other models.

    Attributes
    ----------
    client: :class:`.GatewayClient`
        The client currently in-use.

    data: :class:`dict`
        The data of the object.
    """

    __slots__ = ()

    client: GatewayClient = attr.field(repr=False)
    data: dict[Any, Any] = attr.field(repr=False)

    @staticmethod
    def field(
        *,
        key: None | str = None,
        cls: type[Any] = str,
        has_client: bool = False,
        **kwargs: Any
    ) -> Any:
        """Used as an attribute placeholder.

        Parameters
        ----------
        key: None | :class:`str`
            The key to use when initializing the instance.

        cls: :class:`type`
            The class to create the attribute with.

        has_client: :class:`bool`
            If the class being used needs :class:`.GatewayClient` to be passed.

        constructor: Callable[..., Any]
            The constructor to use.

        check: Callable[..., bool]
            A check that items need to pass when passed a list.

        kwargs: Any
            Extra options to pass when calling :meth:`attr.field`.
        """
        return attr.field(
            init=False,
            default=kwargs.pop("default", None),
            repr=kwargs.pop("repr", False),
            metadata={
                "key": key,
                "cls": cls,
                "has_client": has_client,
                "constructor": kwargs.pop("constructor", None),
                "check": kwargs.pop("check", None),
            },
            **kwargs,
        )

    def serialize(self) -> dict[Any, Any]:
        """Turns the object into a dict.
        Intended to be in tandem with :meth:`.GatewayClient.unserialize`.
        """
        return self.data

    def __attrs_post_init__(self) -> None:
        for attribute in attr.fields(self.__class__):
            if attribute.name in {"client", "data"}:
                continue

            metadata = attribute.metadata
            value = self.data.get(metadata["key"] or attribute.name)
            class_type = metadata["cls"]

            if value is None:
                setattr(self, attribute.name, attribute.default)
                continue

            construct = (
                (
                    functools.partial(class_type, self.client)
                    if metadata["has_client"]
                    else functools.partial(class_type)
                )
                if not metadata["constructor"]
                else (
                    functools.partial(metadata["constructor"], self.client)
                    if metadata["has_client"]
                    else functools.partial(metadata["constructor"])
                )
            )

            if isinstance(value, list):
                items: list[Any] = value
                check: Callable[..., bool] = metadata["check"] or (lambda *_: True)

                setattr(
                    self,
                    attribute.name,
                    [construct(item) for item in items if check(item)],
                )
                continue

            setattr(self, attribute.name, construct(value))

        if isinstance(self, Cacheable) and getattr(self, "id", None) is not None:
            self.__class__.cache.set(getattr(self, "id"), self)
