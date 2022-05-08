from __future__ import annotations

from typing import Any
from uuid import uuid4

import attr

from .text import TextInput
from .types import ComponentType

__all__ = ("Modal",)


class ModalMeta(type):
    __components__: list[TextInput]

    def __new__(
        cls: type[ModalMeta],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[Any, Any],
    ) -> ModalMeta:
        components: list[TextInput] = []

        for value in attrs.copy().values():
            if isinstance(value, TextInput):
                components.append(value)

        attrs["__components__"] = components
        return super().__new__(cls, name, bases, attrs)


@attr.s()
class Modal(metaclass=ModalMeta):
    """Represents a modal component.

    title: :class:`str`
        The title of the modal.

    custom_id: :class:`str`
        The custom ID of the modal.

    components: :class:`list`
        A list of the modal's components.
    """

    __components__: list[TextInput] = attr.field(init=False)

    title: str = attr.field()
    custom_id: str = attr.field(default=uuid4().hex)
    components: list[TextInput] = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.components = []
        self.add(*self.__components__)

    def add(self, *components: TextInput) -> None:
        """Adds components to the action row.

        Parameters
        ----------
        components: :class:`.TextInput`
            The text input instances to add to the action row.
        """
        self.components.extend(components)

    def to_dict(self) -> dict[str, str | list[dict[Any, Any]]]:
        """Turns the Modal into a use-able dict.

        Returns
        -------
        :class:`dict`
            The dictionary representation of the action row.
        """
        return {
            "title": self.title,
            "custom_id": self.custom_id,
            "components": [
                {
                    "type": int(ComponentType.ACTIONROW),
                    "components": [c.to_dict() for c in self.components],
                }
            ],
        }
