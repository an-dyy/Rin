__author__: str = ...
__license__: str = ...
__version__: str = ...

from typing import Literal, NamedTuple

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

version: Version = ...
