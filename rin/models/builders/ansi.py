from __future__ import annotations

import enum
from itertools import cycle
from typing import Any

import attr

__all__ = (
    "Mode",
    "Color",
    "ANSIBuilder",
)


class Mode(str, enum.Enum):
    """Mode enum. Holds all supported ANSI modes.

    Attributes
    ----------
    ESCAPE: :class:`str`
        The ANSI escape unicode.

    RESET: :class:`str`
        The ANSI escape reset code.

    BOLD: :class:`str`
        The ANSI escape bold code.

    DIM: :class:`str`
        The ANSI escape dim code.

    UNDERLINE: :class:`str`
        The ANSI escape underline code.
    """

    ESCAPE = "\u001b"
    RESET = "\u001b[0m"
    BOLD = "\u001b[1"
    DIM = "\u001b[2"
    UNDERLINE = "\u001b[4"


class Color(tuple[int, int], enum.Enum):
    """Color enum. Holds all supported ANSI colors.

    Each enum contains a tuple of two elements, the first being
    the forground color code, and the second being the background color code.

    Attributes
    ----------
    BLACK: :class:`tuple`
        The black color codes.

    RED: :class:`tuple`
        The red color codes.

    GREEN: :class:`tuple`
        The green color codes.

    YELLOW: :class:`tuple`
        The yellow color codes.

    BLUE: :class:`tuple`
        The blue color codes.

    MAGENTA: :class:`tuple`
        The magenta color codes.

    CYAN: :class:`tuple`
        The cyan color codes.

    WHITE: :class:`tuple`
        The white color codes.

    DEFAULT: :class:`tuple`
        The default color code.
    """

    BLACK = 30, 40
    RED = 31, 41
    GREEN = 32, 42
    YELLOW = 33, 43
    BLUE = 34, 44
    MAGENTA = 35, 45
    CYAN = 36, 46
    WHITE = 37, 47
    DEFAULT = 39, 49


@attr.s(slots=True)
class ANSIBuilder:
    """A helper class to build ANSI codeblocks.

    Attributes
    ----------
    lines: :class:`list`
        A list of :class:`str` which have been created.
        This will be all joined together when finalizing the construction.
    """

    lines: list[str] = []

    def __enter__(self) -> ANSIBuilder:
        return self

    def __exit__(self, *_: Any) -> None:
        self.clear()

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        self.new(*args, **kwargs)

    def new(
        self,
        text: str,
        *,
        mode: Mode = Mode.BOLD,
        fore: Color = Color.DEFAULT,
        back: Color = Color.DEFAULT,
        reset_after: bool = True,
        new_line: bool = True,
    ) -> None:
        """Creates a new string using the mode passed in.

        Parameters
        ----------
        text: :class:`str`
            The message to color/style.

        mode: :class:`.Mode`
            The mode to use, E.g `BOLD`, `DIM` etc.

        fore: :class:`.Color`
            The foreground color to use.

        back: :class:`.Color`
            The background color to use.

        reset_after: :class:`bool`
            If a reset code should be added after adding the new line.

        new_line: :class:`bool`
            If a new line should be added after adding this one.
        """
        self.lines.append(f"{mode};{fore[0]};{back[1]}m{text}")

        if reset_after is not False:
            self.lines.append(Mode.RESET)

        if new_line is True:
            self.lines.append("\n")

    def colorful(self, text: str, *, mode: Mode = Mode.BOLD) -> None:
        """Turns a string into a colorful one.

        Parameters
        ----------
        text: :class:`str`
            The text to turn colorful.

        mode: :class:`.Mode`
            The mode to use for the text.
        """
        self.lines.append(Mode.RESET)

        for color, char in zip(cycle(Color), text):
            self.lines.append(f"{mode};{color[0]}m{char}")

        self.lines.append("\n")

    def clear(self) -> None:
        """Clears the current lines of the builder."""
        self.lines.clear()

    @property
    def text(self) -> str:
        """A string form of all the messages currently
        inside of the builders lines.
        """
        return "".join(self.lines)

    @property
    def final(self) -> str:
        """Returns an ANSI codeblock with the string form
        of the builder.
        """
        return f"```ansi\n{self.text}\n```"
