from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Listing:
    id: str
    portal: str
    title: str
    price: int
    url: str
    image: Optional[str] = None
    location: Optional[str] = None
    mileage: Optional[str] = None
    year: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)

    @property
    def composite_id(self) -> str:
        return f"{self.portal}_{self.id}"


@dataclass(frozen=True)
class SearchQuery:
    id: str
    portal: str
    url: str

