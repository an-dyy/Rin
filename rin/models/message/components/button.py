from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Coroutine
from uuid import uuid4

import attr
from typing_extensions import Self

from ...guild import PartialEmoji
from .cache import ComponentCache
from .types import ButtonStyle, ComponentType

if TYPE_CHECKING:
    from ...interactions import Interaction

__all__ = ("Button", "button")


@attr.s()
class Button:
    """Represents a button component.

    Attributes
    ----------
    label: :class:`str`
        The label of the button.

    style: :class:`.ButtonStyle`
        The styling of the button.

    custom_id: :class:`str`
        The custom ID of the button.

    url: None | :class:`str`
        The url of the button.

    emoji: None | :class:`.PartialEmoji`
        The emoji to use for the button.

    disabled: :class:`bool`
        If the button is disabled.
    """

    label: str = attr.field()
    style: ButtonStyle = attr.field(default=ButtonStyle.PRIMARY)
    custom_id: str = attr.field(default=uuid4().hex)

    url: None | str = attr.field(default=None)
    emoji: None | PartialEmoji = attr.field(default=None)
    disabled: bool = attr.field(default=False)

    type: ComponentType = attr.field(init=False, default=ComponentType.BUTTON)

    def __attrs_post_init__(self) -> None:
        if self.url is not None and self.type is not ButtonStyle.LINK:
            raise TypeError("Can only use URL when using `ButtonStyle.LINK`") from None

        ComponentCache.cache.set(self.custom_id, self)

    def set_callback(self, func: Callable[..., Coroutine[Any, Any, Any]]) -> Self:
        setattr(self, "callback", func)
        return self

    async def callback(self, interaction: Interaction, component: Self) -> Any:
        return NotImplemented

    def to_dict(self) -> dict[str, str | int | bool | dict[Any, Any]]:
        payload: dict[str, str | int | bool | dict[Any, Any]] = {
            "style": int(self.style),
            "type": int(self.type),
            "label": self.label,
            "custom_id": self.custom_id,
            "disabled": self.disabled,
        }

        if self.style is ButtonStyle.LINK:
            del payload["custom_id"]

        if self.emoji is not None:
            payload["emoji"] = {
                "name": self.emoji.name,
                "id": self.emoji.id,
                "animated": self.emoji.animated,
            }

        return payload


def button(
    label: str,
    style: ButtonStyle,
    custom_id: None | str = None,
    emoji: None | PartialEmoji = None,
    url: None | str = None,
    disabled: bool = False,
) -> Callable[..., Button]:
    """Creates a button component.
    Sets the wrapped function as the button's callback.

    Parameters
    label: :class:`str`
        The label of the button.

    style: :class:`.ButtonStyle`
        The styling of the button.

    custom_id: None | :class:`str`
        The custom ID of the button.

    url: None | :class:`str`
        The url of the button.

    emoji: None | :class:`.PartialEmoji`
        The emoji to use for the button.

    disabled: :class:`bool`
        If the button is disabled.
    """

    def inner(func: Callable[..., Coroutine[Any, Any, Any]]) -> Button:
        return Button(
            label, style, custom_id or uuid4().hex, url, emoji, disabled
        ).set_callback(func)

    return inner
