from abc import ABC, abstractmethod
from ..core.models import Listing

class Notifier(ABC):
    @abstractmethod
    async def notify_new(self, listing: Listing, search_id: str):
        pass

    @abstractmethod
    async def notify_price_drop(self, listing: Listing, old_price: int, search_id: str):
        pass

NOTIFIERS_REGISTRY: dict[str, type[Notifier]] = {}

def register_notifier(name: str):
    def decorator(cls):
        NOTIFIERS_REGISTRY[name] = cls
        return cls
    return decorator

