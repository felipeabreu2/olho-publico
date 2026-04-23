from abc import ABC, abstractmethod
from collections.abc import Iterator

from pydantic import BaseModel


class Source(ABC):
    """Base class for all data sources.

    Each source knows how to:
    - Download / fetch its raw data
    - Yield validated Pydantic records
    """

    name: str

    @abstractmethod
    def fetch(self) -> Iterator[BaseModel]:
        """Yield validated records from this source."""
