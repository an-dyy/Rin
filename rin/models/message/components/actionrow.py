from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

import attr
from typing_extensions import Self

from .types import ComponentType

if TYPE_CHECKING:
    from ...interactions import Interaction

__all__ = ("Component", "ActionRow")


@runtime_checkable
class Component(Protocol):
    """A protocol class for components.

    Attributes
    ----------
    custom_id: :class:`str`
        The customn ID of the component.
    """

    custom_id: str

    def to_dict(self) -> dict[Any, Any]:
        """Turns the component into a use-able dict.

        Returns
        -------
        :class:`dict`
            The dictionary representation of the component.
        """
        return {}

    async def callback(self, interaction: Interaction, component: Self) -> Any:
        """The callback to run when a component is triggered.

        Parameters
        ----------
        interaction: :class:`.Interaction`
            The interaction that fired the component.

        component: :class:`.Component`
            The component that got fired.
        """
        return NotImplemented


class ActionRowMeta(type):
    __components__: list[Component]

    def __new__(
        cls: type[ActionRowMeta],
        name: str,
        bases: tuple[type, ...],
        attrs: dict[Any, Any],
    ) -> ActionRowMeta:
        components: list[Component] = []

        for value in attrs.copy().values():
            if isinstance(value, Component):
                components.append(value)

        attrs["__components__"] = components
        return super().__new__(cls, name, bases, attrs)


@attr.s(slots=True)
class ActionRow(metaclass=ActionRowMeta):
    """Represents an Action row.
    This model is a container for other components.

    Attributes
    ----------
    type: :class:`.ComponentType`
        Always a type of ``1``.

    components: :class:`list`
        A list of :class:`.Component` currently inside of the
        action row.
    """

    __components__: list[Component] = attr.field(init=False)

    type: ComponentType = attr.field(init=False, default=ComponentType.ACTIONROW)
    components: list[Component] = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        self.components = []
        self.add(*self.__components__)

    def add(self, *components: Component) -> None:
        """Adds components to the action row.

        Parameters
        ----------
        components: :class:`.Component`
            The components instance to add to the action row.
        """
        self.components.extend(components)

    def to_dict(self) -> dict[str, int | list[dict[Any, Any]]]:
        """Turns the Action row into a use-able dict.

        Returns
        -------
        :class:`dict`
            The dictionary representation of the action row.
        """
        return {
            "type": int(self.type),
            "components": [c.to_dict() for c in self.components],
        }
