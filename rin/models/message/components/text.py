from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Coroutine, cast
from uuid import uuid4

import attr

from .actionrow import Component
from .cache import ComponentCache
from .types import ComponentType, TextInputStyle

if TYPE_CHECKING:
    from ...interactions import Interaction

__all__ = ("TextInput", "text")


@attr.s()
class TextInput:
    """Represents a TextInput component.

    Attributes
    ----------
    label: :class:`str`
        The label of the text input.

    style: :class:`.TextInputStyle`
        The style of the text input.

    custom_id: :class:`str`
        The custom ID of the text input.

    min_length: :class:`int`
        The minimum length of the response required for the input.

    max_length: :class:`int`
        The maximum length of the response required for the input.

    required: :class:`bool`
        If it is required to respond to the text input.

    placeholder: None | :class:`str`
        The placeholder to show when no value is given.

    value: None | :class:`str`
        The pre-filled value of the text input.
    """

    label: str = attr.field()
    style: TextInputStyle = attr.field()
    custom_id: str = attr.field(default=uuid4().hex)

    min_length: int = attr.field(default=0)
    max_length: int = attr.field(default=4000)

    required: bool = attr.field(default=True)
    placeholder: None | str = attr.field(default=None)
    value: None | str = attr.field(default=None)

    type: ComponentType = attr.field(init=False, default=ComponentType.TEXTINPUT)

    def __attrs_post_init__(self) -> None:
        ComponentCache.cache.set(self.custom_id, cast(Component, self))

    def set_callback(self, func: Callable[..., Coroutine[Any, Any, Any]]) -> TextInput:
        setattr(self, "callback", func)
        return self

    async def callback(self, interaction: Interaction, input: str) -> Any:
        return NotImplemented

    def to_dict(self) -> dict[str, str | int | bool]:
        payload = {
            "type": int(self.type),
            "style": int(self.style),
            "label": self.label,
            "custom_id": self.custom_id,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "required": self.required,
        }

        if self.placeholder is not None:
            payload["placeholder"] = self.placeholder

        if self.value is not None:
            payload["value"] = self.value

        return payload


def text(
    label: str,
    style: TextInputStyle,
    custom_id: str = uuid4().hex,
    min_length: int = 0,
    max_length: int = 4000,
    required: bool = True,
    placeholder: None | str = None,
    value: None | str = None,
) -> Callable[..., TextInput]:
    """Creates a TextInput component.
    Sets the wrapped function as the text input's callback.

    Parameters
    ----------
    label: :class:`str`
        The label of the text input.

    style: :class:`.TextInputStyle`
        The style of the text input.

    custom_id: :class:`str`
        The custom ID of the text input.

    min_length: :class:`int`
        The minimum length of the response required for the input.

    max_length: :class:`int`
        The maximum length of the response required for the input.

    required: :class:`bool`
        If it is required to respond to the text input.

    placeholder: None | :class:`str`
        The placeholder to show when no value is given.

    value: None | :class:`str`
        The pre-filled value of the text input.
    """

    def inner(func: Callable[..., Coroutine[Any, Any, Any]]) -> TextInput:
        return TextInput(
            label=label,
            style=style,
            custom_id=custom_id,
            min_length=min_length,
            max_length=max_length,
            required=required,
            placeholder=placeholder,
            value=value,
        ).set_callback(func)

    return inner
