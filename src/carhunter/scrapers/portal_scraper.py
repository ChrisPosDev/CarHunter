import logging
from typing import AsyncIterator
from urllib.parse import urljoin
from ..core.models import Listing
from ..core.exceptions import StrategyError, FetchError
from ..config.schema import PortalConfig
from ..http.client import HttpClient
from .base import STRATEGY_REGISTRY

logger = logging.getLogger(__name__)

class PortalScraper:
    def __init__(self, config: PortalConfig, http_client: HttpClient):
        self.config = config
        self.http_client = http_client

    async def fetch_listings(self, url: str) -> list[Listing]:
        html = await self.http_client.get(url)
        
        for strategy_config in self.config.strategies:
            strategy_class = STRATEGY_REGISTRY.get(strategy_config.type)
            if not strategy_class:
                logger.error(f"Unknown strategy type: {strategy_config.type}")
                continue
                
            strategy = strategy_class()
            listings = []
            try:
                logger.debug(f"Trying strategy {strategy_config.type} for {url}")
                async for listing in strategy.extract(html, strategy_config, self.config.name):
                    # Normalize URL
                    if listing.url and not listing.url.startswith('http'):
                        listing = Listing(
                            **{**listing.__dict__, 'url': urljoin(self.config.base_url, listing.url)}
                        )
                    listings.append(listing)
                    
                if listings:
                    logger.info(f"Strategy {strategy_config.type} succeeded, found {len(listings)} listings")
                    return listings
                else:
                    logger.debug(f"Strategy {strategy_config.type} returned no listings")
            except StrategyError as e:
                logger.warning(f"Strategy {strategy_config.type} failed: {e}")
                
        raise StrategyError(f"All strategies failed for portal {self.config.name} at URL {url}")

