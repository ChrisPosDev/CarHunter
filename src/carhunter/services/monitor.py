import asyncio
import logging
import random
from typing import Dict, List
from ..core.events import EventBus
from ..core.models import SearchQuery, Listing
from ..config.schema import Settings, PortalConfig
from ..storage.sqlite import SqliteListingRepository
from ..scrapers.portal_scraper import PortalScraper
from ..http.client import HttpClient

logger = logging.getLogger(__name__)

class MonitorService:
    def __init__(
        self, 
        settings: Settings, 
        portals: Dict[str, PortalConfig],
        repository: SqliteListingRepository,
        event_bus: EventBus,
        http_client: HttpClient
    ):
        self.settings = settings
        self.portals = portals
        self.repository = repository
        self.event_bus = event_bus
        self.http_client = http_client
        self._running = False
        
        self.scrapers = {
            name: PortalScraper(config, http_client)
            for name, config in portals.items()
        }
        self._initialized_searches: set[str] = set()

    async def start(self):
        self._running = True
        logger.info("Starting MonitorService")
        
        while self._running:
            for search_config in self.settings.searches:
                if search_config.portal not in self.settings.active_portals:
                    continue
                
                try:
                    await self._check_search(search_config)
                except Exception as e:
                    logger.error(f"Error checking search {search_config.id}: {e}")
                    
                # Small delay between searches to be polite
                await asyncio.sleep(2)
            
            # Wait for next interval with jitter
            interval = self.settings.monitor.check_interval_seconds
            jitter = random.randint(0, self.settings.monitor.jitter_seconds)
            wait_time = interval + jitter
            logger.info(f"Waiting {wait_time} seconds until next check")
            await asyncio.sleep(wait_time)

    def stop(self):
        self._running = False

    async def _check_search(self, search_config):
        scraper = self.scrapers.get(search_config.portal)
        if not scraper:
            logger.error(f"No scraper found for portal: {search_config.portal}")
            return

        logger.info(f"Checking {search_config.id} on {search_config.portal}")
        listings = await scraper.fetch_listings(search_config.url)
        
        is_baseline = search_config.id not in self._initialized_searches

        if is_baseline:
            logger.info(f"Initial run for {search_config.id} - saving baseline of {len(listings)} listings without notifications.")
            for listing in listings:
                await self.repository.save(listing)
            self._initialized_searches.add(search_config.id)
            return
        
        for listing in listings:
            exists = await self.repository.exists(listing.composite_id)
            if not exists:
                logger.info(f"New listing found: {listing.title} ({listing.price} PLN)")
                await self.repository.save(listing)
                await self.event_bus.publish("new_listing", listing, search_config.id)
            else:
                old_price = await self.repository.get_price(listing.composite_id)
                if old_price is not None and listing.price < old_price:
                    logger.info(f"Price drop for {listing.title}: {old_price} -> {listing.price}")
                    await self.repository.save(listing) # Update price
                    await self.event_bus.publish("price_drop", listing, old_price, search_config.id)

