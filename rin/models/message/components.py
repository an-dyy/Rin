from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Callable

import attr

from ..cacheable import Cache, Cacheable
from .types import ButtonStyle, ComponentType

if TYPE_CHECKING:
    from ..interactions import Interaction

__all__ = ("ActionRow", "Button", "button", "Component")


class Component(Cacheable):
    custom_id: str
    cache: Cache[Button]

    def to_dict(self) -> dict[Any, Any]:
        raise NotImplementedError

    async def callback(self, interaction: Interaction, component: Component) -> Any:
        raise NotImplementedError


@attr.s(slots=True)
class ActionRow:
    children: list[Button] = attr.field()

    def to_dict(self) -> dict[Any, Any]:
        return {
            "type": ComponentType.ACTIONROW,
            "components": [c.to_dict() for c in self.children],
        }


@attr.s(slots=True)
class Button:
    style: ButtonStyle = attr.field()
    label: str = attr.field()
    custom_id: str = attr.field(default=uuid.uuid4().hex)

    disabled: bool = attr.field(default=False)
    emoji: None | str = attr.field(default=None)
    url: None | str = attr.field(default=None)

    type: int = attr.field(init=False, default=2)
    callback: Callable[..., Any] = attr.field(init=False)

    def __attrs_post_init__(self) -> None:
        Component.cache.set(self.custom_id, self)

    def to_dict(self) -> dict[Any, Any]:
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


def button(
    label: str,
    style: ButtonStyle,
    custom_id: str = uuid.uuid4().hex,
    disabled: bool = False,
    emoji: None | str = None,
    url: None | str = None,
) -> Callable[..., Button]:
    """Creates a button.

    Uses the decorated function as the button's callback.
    This function should take two arguments, :class:`.Interaction` and :class:`.Button`

    Examples
    --------
    .. code:: python
        @button("Foo!", rin.ButtonStyle.PRIMARY)
        async def callback(interaction: Interaction, button: Button) -> None:
            await interaction.send("Bar!")
    """

    def inner(func: Callable[..., Any]) -> Button:
        button = Button(style, label, custom_id, disabled, emoji, url)
        button.callback = func

        return button

    return inner
