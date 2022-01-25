from __future__ import annotations

from typing import TYPE_CHECKING, Any

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
        *, key: str, cls: type[Any] = str, has_client: bool = False, **kwargs: Any
    ) -> Any:
        """Used as an attribute placeholder.

        Parameters
        ----------
        key: :class:`str`
            The key to use when initializing the instance.

        cls: :class:`type`
            The class to create the attribute with.

        has_client: :class:`bool`
            If the class being used needs :class:`.GatewayClient` to be passed.

        kwargs: Any
            Extra options to pass when calling :meth:`attr.field`.
        """
        return attr.field(
            init=False,
            metadata={"key": key, "cls": cls, "has_client": has_client},
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

            data = attribute.metadata
            if value := self.data.get(data["key"]):
                if data["has_client"] is True:
                    setattr(self, attribute.name, data["cls"](self.client, value))
                    continue

                setattr(self, attribute.name, data["cls"](value))

            elif value is None:
                setattr(
                    self,
                    attribute.name,
                    attribute.default
                    if attribute.default is not attr.NOTHING
                    else value,
                )

        if isinstance(self, Cacheable) and getattr(self, "id", None) is not None:
            self.__class__.cache.set(getattr(self, "id"), self)
