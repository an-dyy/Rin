from __future__ import annotations

from typing import Any

__all__ = ("HTTPException", "Unauthorized", "BadRequest", "Forbidden", "NotFound")


class HTTPException(Exception):
    """Represents an error when making a request.

    Parameters
    ----------
    data: dict[str, Any]
        The data of the error received from the RESTful API.

    Attributes
    ----------
    data: dict[str, Any]
        The data of the error.
    """

    def __init__(self, data: dict[str, Any] | str) -> None:
        self.data = data
        super().__init__(f"{self.message!r}")

    def __repr__(self) -> str:
        return f"{self.message!r} data: {self.data} code: {self.code}"

    @property
    def code(self) -> int:
        """The error's code."""
        return 0 if isinstance(self.data, str) else self.data.get("code", 0)

    @property
    def message(self) -> str:
        """The error's message."""
        return self.data if isinstance(self.data, str) else self.data.get("message", "")


class Unauthorized(HTTPException):
    """Represents a 401 HTTP error."""

    pass


class BadRequest(HTTPException):
    """Represents a 400 HTTP error."""

    pass


class Forbidden(HTTPException):
    """Represents a 403 HTTP error."""

    pass


class NotFound(HTTPException):
    """Represents a 404 HTTP error."""

    pass
