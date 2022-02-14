from __future__ import annotations

import io
import os
from typing import BinaryIO

import attr

__all__ = ("File",)


@attr.s(slots=True)
class File:
    """A helper class for files.

    Parameters
    ----------
    fp: :class:`str` | :class:`os.PathLike` | :class:`bytes`
        The file path of the class, or source.

    name: None | :class:`str`
        The name of the file.

    Attributes
    ----------
    fp: :class:`str` | :class:`os.PathLike` | :class:`bytes`
        The file path of the class, or source.

    name: None | :class:`str`
        The name of the file.

    source: :class:`bytes`
        The source of the file.
    """

    fp: str | os.PathLike[str] | BinaryIO = attr.field(repr=False)
    name: None | str = attr.field(default=None, repr=True)
    source: io.BufferedReader | BinaryIO = attr.field(init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        if isinstance(self.fp, (str, os.PathLike)):
            self.source = open(self.fp, "rb")

        elif isinstance(self.fp, BinaryIO):
            self.source = self.fp

        self.name = self.name or getattr(self.source, "name", None)

    def read(self, size: None | int) -> bytes:
        """Reads the bytes of the file.

        Parameters
        ----------
        size: None | :class:`int`
            The size of bytes to read up to.

        Returns
        -------
        :class:`bytes`
            The read bytes.
        """
        return self.source.read(size or -1)

    def close(self) -> None:
        """Closes the file."""
        return self.source.close()
