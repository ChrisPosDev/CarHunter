from typing import Callable, Any, Awaitable
from collections import defaultdict
import asyncio
from .models import Listing

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable[..., Awaitable[Any]]]] = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable[..., Awaitable[Any]]):
        self._subscribers[event_type].append(callback)

    async def publish(self, event_type: str, *args, **kwargs):
        callbacks = self._subscribers.get(event_type, [])
        if not callbacks:
            return
        
        # Run all callbacks concurrently
        await asyncio.gather(
            *[callback(*args, **kwargs) for callback in callbacks],
            return_exceptions=True
        )

