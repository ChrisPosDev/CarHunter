import httpx
import os
import logging
from .base import Notifier, register_notifier
from ..core.models import Listing

logger = logging.getLogger(__name__)

@register_notifier("discord")
class DiscordNotifier(Notifier):
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        if not self.webhook_url:
            logger.warning("DISCORD_WEBHOOK_URL is not set. Discord notifications will not be sent.")

    async def _send(self, embed: dict):
        if not self.webhook_url:
            return
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.webhook_url,
                    json={"embeds": [embed]}
                )
                response.raise_for_status()
            except Exception as e:
                logger.error(f"Failed to send Discord notification: {e}")

    async def notify_new(self, listing: Listing, search_id: str):
        embed = {
            "title": f"🚗 Nowe ogłoszenie: {listing.title}",
            "url": listing.url,
            "color": 0x00FF00, # Green
            "fields": [
                {"name": "Cena", "value": f"{listing.price} PLN", "inline": True},
                {"name": "Portal", "value": listing.portal, "inline": True},
                {"name": "Szukajka", "value": search_id, "inline": True},
            ],
            "footer": {"text": "CarHunter"}
        }
        if listing.image:
            embed["image"] = {"url": listing.image}
            
        await self._send(embed)

    async def notify_price_drop(self, listing: Listing, old_price: int, search_id: str):
        embed = {
            "title": f"📉 Spadek ceny: {listing.title}",
            "url": listing.url,
            "color": 0xFF0000, # Red
            "fields": [
                {"name": "Nowa Cena", "value": f"{listing.price} PLN", "inline": True},
                {"name": "Stara Cena", "value": f"~~{old_price} PLN~~", "inline": True},
                {"name": "Szukajka", "value": search_id, "inline": True},
            ],
            "footer": {"text": "CarHunter"}
        }
        if listing.image:
            embed["image"] = {"url": listing.image}
            
        await self._send(embed)

