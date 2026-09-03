from abc import ABC, abstractmethod
from typing import List, Optional
from models import ImageCandidate

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Return True if this provider is enabled and configured."""
        pass

    @abstractmethod
    async def search(self, character_name: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        """
        Search and return candidate images for the given character.
        Supports popularity sorting, pagination, and strict rating filtering ('sfw' vs 'r18').
        Must respect source licensing and not bypass anti-bot mechanisms.
        """
        pass
