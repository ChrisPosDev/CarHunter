from abc import ABC, abstractmethod
from typing import AsyncIterator
from ..core.models import Listing
from ..config.schema import StrategyConfig

class FetchStrategy(ABC):
    @abstractmethod
    async def extract(self, html: str, config: StrategyConfig, portal_name: str) -> AsyncIterator[Listing]:
        """Extracts listings from HTML or API response."""
        yield # Make it async generator
        pass

STRATEGY_REGISTRY: dict[str, type[FetchStrategy]] = {}

def register_strategy(name: str):
    def decorator(cls):
        STRATEGY_REGISTRY[name] = cls
        return cls
    return decorator

