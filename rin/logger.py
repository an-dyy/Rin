from __future__ import annotations

from typing import Any, ClassVar
from logging import StreamHandler, LogRecord, Formatter, DEBUG, getLogger, Logger

__all__ = ["ColouredStreamHandler", "create"]


class ColouredStreamHandler(StreamHandler):
    """A ColouredStreamHandler that uses the built-in logging module's but adds colours.
    This is a simple wrapper around the built-in logging module's StreamHandler class.
    """

    COLOUR_MAP: ClassVar[dict[str, str]] = {
        "INFO": "\u001b[32m{}\u001b[0m",
        "DEBUG": "\u001b[32m{}\u001b[0m",
        "WARNING": "\u001b[32m\u001b[33m{}\u001b[0m",
        "ERROR": "\u001b[31m{}\u001b[0m",
        "CRITICAL": "\u001b[0;91m{}\u001b[0m",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.formatter = Formatter("[%(levelname)s] :: %(message)s")

    def emit(self, record: LogRecord) -> None:
        """Emit a record.

        Parameters
        ----------
        record: :class:`LogRecord`
            The record to emit.
        """
        if colour := self.COLOUR_MAP.get(record.levelname):
            record.levelname = colour.format(record.levelname)

        return super().emit(record)


def create(
    name: str,
    level: int = DEBUG,
    *,
    cls: type[StreamHandler[Any]] = ColouredStreamHandler,
) -> Logger[Any]:
    """Creates a logger with the given name and level.

    Parameters
    ----------
    name: :class:`str`
        The name of the logger.

    level: :class:`int`
        The level of the logger.

    cls: :class:`type`
        The handler class to use.

    Returns
    -------
    :class:`logging.Logger`
        The created logger.
    """
    logger = getLogger(name)

    logger.addHandler(cls())
    logger.setLevel(level)

    return logger
