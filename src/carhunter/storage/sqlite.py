import aiosqlite
from pathlib import Path
from ..core.models import Listing

class SqliteListingRepository:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    composite_id TEXT PRIMARY KEY,
                    id TEXT,
                    portal TEXT,
                    title TEXT,
                    price INTEGER,
                    url TEXT,
                    image TEXT,
                    location TEXT,
                    mileage TEXT,
                    year TEXT,
                    discovered_at TIMESTAMP
                )
            """)
            await db.commit()

    async def exists(self, composite_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM listings WHERE composite_id = ?", (composite_id,)) as cursor:
                return await cursor.fetchone() is not None

    async def get_price(self, composite_id: str) -> int | None:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT price FROM listings WHERE composite_id = ?", (composite_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def save(self, listing: Listing):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO listings 
                (composite_id, id, portal, title, price, url, image, location, mileage, year, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                listing.composite_id, listing.id, listing.portal, listing.title, 
                listing.price, listing.url, listing.image, 
                listing.location, listing.mileage, listing.year,
                listing.discovered_at
            ))
            await db.commit()

