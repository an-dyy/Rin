from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast, get_args

import attr

if TYPE_CHECKING:
    from ..client import GatewayClient

AttrT = TypeVar("AttrT")
__all__ = ("BaseModel",)


@attr.s(slots=True, hash=True)  # type: ignore
class BaseModel:
    __slots__ = ()

    client: "GatewayClient" = attr.field(repr=False)
    data: dict[str, Any] = attr.field(repr=False)

    @staticmethod
    def field(key: None | str = None, type: type[Any] = str, **kwargs: Any) -> Any:
        """Sets a field for the class.

        Acts as almost a placeholder value. Actual value is set on construction.

        Parameters
        ----------
        key: None | :class:`str`
            The key to do the data lookup with.

        type: :class:`type`
            The type to use when constructing.

        kwargs: Any
            Extra options to pass to :meth:`attr.field`.
        """
        metadata = {"key": key, "type": type}
        metadata["builder"] = kwargs.pop("builder", None)
        metadata.pop("key")

        return attr.field(
            init=kwargs.pop("init", False),
            metadata=BaseModel.parse(key, **metadata, **kwargs),
            **kwargs,
        )

    @staticmethod
    def parse(key: None | str, **kwargs: Any) -> dict[Any, Any]:
        return {"key": key, **kwargs}

    @staticmethod
    def property(
        key: None | str, type: type[Any] = str, **kwargs: Any
    ) -> Callable[..., Any]:
        """Sets a property of the class. Used for adding a constructor.

        Parameters
        ----------
        key: None | :class:`str`
            The key to do the data lookup from.

        type: :class:`type`
            The type to use when constructing.

        kwargs: Any
           Extra arguments to pass to :meth:`attr.field`.
        """

        def inner(func: Callable[..., Any]) -> Any:
            return BaseModel.field(key, type, builder=func, **kwargs)

        return inner

    def construct(self) -> None:
        """This method actually handles construction of attributes.

        This method will iterate through all the fields specified on this class.
        It will then check the type of the field by looking through the metadata.
        """
        for attribute in attr.fields(self.__class__):

            if attribute.name in {"client", "data"}:
                continue

            data = self.data.get(attribute.metadata["key"] or attribute.name)
            type = attribute.metadata["type"]

            if data is None:
                setattr(self, attribute.name, None)
                continue

            elif issubclass(type, BaseModel):
                setattr(self, attribute.name, type(self.client, data or {}))
                continue

            elif builder := attribute.metadata.get("builder"):
                setattr(self, attribute.name, builder(self, self.client, data))
                continue

            elif callable(type):
                builtin = type.__class__.__module__ == "builtins"
                if not builtin and len(inspect.getargspec(type)[0]) == 0:
                    continue

                if isinstance(data, list):
                    data = type([get_args(type)[0](val) for val in cast(Any, data)])

                    setattr(self, attribute.name, data)
                    continue

                setattr(self, attribute.name, type(data))

    def __attrs_post_init__(self) -> None:
        self.construct()
