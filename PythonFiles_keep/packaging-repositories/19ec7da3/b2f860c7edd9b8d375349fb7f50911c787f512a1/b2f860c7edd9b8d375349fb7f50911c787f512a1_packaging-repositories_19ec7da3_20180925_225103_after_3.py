__all__ = [
    "__version__",
    "Fetcher",
    "FlatHTMLRepository", "LocalDirectoryRepository", "SimpleRepository",
]

from .fetchers import Fetcher
from .repositories import (
    FlatHTMLRepository, LocalDirectoryRepository, SimpleRepository,
)

__version__ = "0.1.0"
