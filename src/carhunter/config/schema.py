from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class MonitorConfig(BaseModel):
    check_interval_seconds: int = 60
    jitter_seconds: int = 15

class SearchConfig(BaseModel):
    id: str
    portal: str
    url: str

class Settings(BaseModel):
    monitor: MonitorConfig
    active_portals: List[str]
    active_notifiers: List[str]
    searches: List[SearchConfig]

class StrategyConfig(BaseModel):
    type: str
    items_path: Optional[str] = None
    item_selector: Optional[str] = None
    fields: Dict[str, str]

class PortalConfig(BaseModel):
    name: str
    base_url: str
    strategies: List[StrategyConfig]

