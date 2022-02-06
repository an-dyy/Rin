from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable, Coroutine
from uuid import uuid4

import attr

from ..cacheable import Cache, Cacheable
from .types import ButtonStyle, ComponentType

if TYPE_CHECKING:
    from ..interactions import Interaction

__all__ = (
    "ComponentCache",
    "Component",
    "ActionRowBuilder",
    "Button",
    "SelectMenuBuilder",
    "SelectOption",
)


class ComponentCache(Cacheable):
    """A cache of all the components that are cacheable."""

    cache: Cache[Component]


class Component:
    """A base component class.

    Attributes
    ----------
    custom_id: str
        The custom id of the component.

    type: :class:`.ComponentType`
        The type of the component
    """

    custom_id: str
    type: ComponentType

    async def callback(self, interaction: Interaction, component: Component) -> None:
        """The callback of the component. By default does nothing.

        Parameters
        ----------
        interaction: :class:`.Interaction`
            The interaction which triggered the component.

        component: :class:`.Component`
            The component which was triggered.
        """
        raise NotImplementedError

    def to_dict(self) -> dict[Any, Any]:
        """Creates a dict from the component.

        Returns
        -------
        :class:`dict`
            The dict representing the component.
        """
        raise NotImplementedError


@attr.s(slots=True)
class Button(Component):
    """Represents a button component.

    Parameters
    ----------
    label: :class:`str`
        The label of the button.

    style: :class:`.ButtonStyle`
        The style of the button

    custom_id: :class:`str`
        The custom id of the button.

    disabled: :class:`bool`
        Whether or not the button should be disabled.

    emoji: None | :class:`str`
        The emoji to use for the button.

    url: None | :class:`str`
        The url to use for the button.
    """

    label: str = attr.field()
    style: ButtonStyle = attr.field()
    custom_id: str = attr.field()

    disabled: bool = attr.field(default=False)
    emoji: None | str = attr.field(default=None)
    url: None | str = attr.field(default=None)

    type: ComponentType = attr.field(init=False, default=ComponentType.BUTTON)

    def to_dict(self) -> dict[Any, Any]:
        """Turns the button into a dict.

        Returns
        -------
        :class:`dict`
            The dict representing the button.
        """
        payload = {
            "style": self.style,
            "type": ComponentType.BUTTON,
            "custom_id": self.custom_id,
            "label": self.label,
            "disabled": self.disabled,
        }

        if self.emoji is not None:
            payload["emoji"] = self.emoji

        if self.url is not None:
            payload["url"] = self.url

        return payload

    async def callback(self, interaction: Interaction, button: Button) -> None:
        """The callback of the button. By default does nothing

        Parameters
        ----------
        interaction: :class:`.Interaction`
            The interaction which triggered the component.

        button: :class:`.Button`
            The button which was triggered.
        """
        raise NotImplementedError


@attr.s(slots=True)
class SelectOption:
    """Represents a SelectMenu option.

    Parameters
    ----------
    label: :class:`str`
        The label of the option.

    value: :class:`str`
        The value of the option.

    description: None | :class:`str`
        The description of the option.

    default: :class:`bool`
        Whether or not the option should be the default one.
    """

    label: str = attr.field()
    value: str = attr.field()
    description: None | str = attr.field(default=None)
    default: bool = attr.field(default=False)

    # TODO: Add emoji

    def to_dict(self) -> dict[Any, Any]:
        """Creates a dict from the option.

        Returns
        -------
        :class:`dict`
            The dict representing the option.
        """
        payload = {"label": self.label, "value": self.value}

        if self.description is not None:
            payload["description"] = self.description

        if self.default is True:
            payload["default"] = self.default  # type: ignore

        return payload


@attr.s(slots=True)
class SelectMenuBuilder(Component):
    """Represents a Select Menu.

    Parameters
    ----------
    options: :class:`list`
        A list of :class:`.SelectOption`s to use.

    custom_id: :class:`str`
        The custom id of the select menu.

    placeholder: None | :class:`str`
        The placeholder to use for the select menu.

    min_values: :class:`int`
        The minimum values needed to be selected.

    max_values: :class:`int`
        The maximum values that can be selected.

    disabled: :class:`bool`
        Whether or not the select menu should be disabled.
    """

    options: list[SelectOption] = attr.field(default=None)
    custom_id: str = attr.field(default=uuid4().hex)
    placeholder: None | str = attr.field(default=None)

    min_values: int = attr.field(default=1)
    max_values: int = attr.field(default=1)

    disabled: bool = attr.field(default=False)
    values: list[str] = attr.field(init=False)
    type: ComponentType = attr.field(init=False, default=ComponentType.SELECTMENU)

    def __attrs_post_init__(self) -> None:
        self.options = self.options or []
        self.values = []

    def add(self, *options: SelectOption) -> None:
        """Adds an option to the menu.

        Parameters
        ----------
        options: :class:`.SelectOption`
            The options to add.
        """
        self.options.extend(options)

    def set(self, *options: SelectOption) -> None:
        """Sets the options of the menu.

        Parameters
        ----------
        options: :class:`.SelectOption`
            The options to set.
        """
        self.options = list(options)

    def set_callback(self) -> Callable[..., Callable[..., Coroutine[Any, Any, None]]]:
        """Sets the callback of the select menu."""

        def inner(
            func: Callable[..., Coroutine[Any, Any, None]]
        ) -> Callable[..., Coroutine[Any, Any, None]]:
            self.callback = func
            return func

        return inner

    def option(self, label: str, value: str, **kwargs: Any) -> SelectOption:
        """Creates a new option to the select menu.

        Parameters
        ----------
        label: :class:`str`
            The label to give the option.

        value: :class:`str`
            The value of the option.

        description: None | :class:`str`
            The description of the option.

        default: :class:`bool`
            Whether or not the option is the default one.

        Returns
        -------
        :class:`.SelectOption`
            The created select option.
        """
        option = SelectOption(
            label, value, kwargs.get("description"), kwargs.get("default", False)
        )
        self.add(option)

        return option

    async def callback(self, interaction: Interaction, menu: SelectMenuBuilder) -> None:
        """The callback of the select menu. By default does nothing

        Parameters
        ----------
        interaction: :class:`.Interaction`
            The interaction which triggered the component.

        menu: :class:`.SelectMenuBuilder`
            The button which was triggered.
        """
        raise NotImplementedError

    def to_dict(self) -> dict[Any, Any]:
        """Creates a dict from the select menu.

        Returns
        -------
        :class:`dict`
            The dict representing the select menu.
        """
        payload = {
            "type": ComponentType.SELECTMENU,
            "options": [opt.to_dict() for opt in self.options],
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
        }

        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder

        return payload

    def __enter__(self) -> SelectMenuBuilder:
        return self

    def __exit__(self, *_: Any) -> None:
        ...


@attr.s(slots=True)
class ActionRowBuilder:
    children: list[Component] = attr.field(default=None, repr=False)
    type: ComponentType = attr.field(init=False, default=ComponentType.ACTIONROW)

    def button(
        self, label: str, style: ButtonStyle, **kwargs: Any
    ) -> Callable[..., Button]:
        """Creates a button for the ActionRow.

        Parameters
        ----------
        label: :class:`str`
            The label of the button.

        style: :class:`.ButtonStyle`
            The style of the button.

        custom_id: :class:`str`
            The custom id to use for the button.

        disabled: :class:`bool`
            If the button should be disabled or not.

        emoji: None | :class:`str`
            The emoji to use for the button.

        url: None | :class:`str`
            The url to use for the button.
        """

        def inner(func: Callable[..., Coroutine[Any, Any, None]]) -> Button:
            if not asyncio.iscoroutinefunction(func):
                raise TypeError("Button callback must be a coroutine.") from None

            custom_id = kwargs.get("custom_id", uuid4().hex)
            disabled = kwargs.get("disabled", False)
            emoji = kwargs.get("emoji")
            url = kwargs.get("url")

            button = Button(
                label,
                style,
                custom_id=custom_id,
                disabled=disabled,
                emoji=emoji,
                url=url,
            )

            button.callback = func
            self.add(button)

            return button

        return inner

    def set(self, *components: Component) -> None:
        """Sets the ActionRow's components."""
        self.children = list(components)

    def add(self, *components: Component) -> None:
        """Adds a component to the ActionRow."""
        self.children.extend(components)

    def cache_all(self) -> list[Component]:
        """Caches all of the children of the ActionRow.

        Returns
        -------
        :class:`list`
            A list of all the components.
        """
        for child in self.children:
            ComponentCache.cache.set(child.custom_id, child)

        return self.children

    def build(self) -> dict[str, int | list[dict[Any, Any]]]:
        """Builds the ActionRow.
        Basically turning it into a dict representation.
        """
        return {
            "type": ComponentType.ACTIONROW,
            "components": [child.to_dict() for child in self.children],
        }

    def __attrs_post_init__(self) -> None:
        self.children = self.children or []

    def __iter__(self):
        for item in [
            ("type", ComponentType.ACTIONROW),
            ("components", [child.to_dict() for child in self.children]),
        ]:
            yield item[0], item[1]

    def __enter__(self) -> ActionRowBuilder:
        return self

    def __exit__(self, *_: Any) -> None:
        self.cache_all()
