__author__ = "Andy"
__license__ = "MIT"
__version__ = "0.2.0-alpha"

from typing import Literal, NamedTuple


class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    id: Literal["alpha", "beta", "final"]


version = Version(0, 2, 0, "alpha")
