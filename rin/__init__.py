__author__ = "Andy"
__license__ = "MIT"
__version__ = "0.2.0-alpha"

from typing import Literal, NamedTuple

__all__ = ("version",)


from .states import *
from .rest import *
from .gateway import *
from .models import *
from .events import *
from .intents import *


class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    id: Literal["alpha", "beta", "final"]


version = Version(0, 3, 0, "alpha")
