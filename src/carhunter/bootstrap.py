import logging
from pathlib import Path
from .config.loader import load_settings, load_portal_config
from .core.events import EventBus
from .storage.sqlite import SqliteListingRepository
from .http.client import HttpClient
from .services.monitor import MonitorService
from .notifiers.base import NOTIFIERS_REGISTRY
# Import to register them
from .notifiers import discord
from .scrapers.strategies import next_data, html_css

async def setup_application(project_root: Path) -> tuple[MonitorService, HttpClient, SqliteListingRepository]:
    # Load config
    settings = load_settings(project_root / "config" / "settings.yaml")
    
    portals = {}
    for portal_name in settings.active_portals:
        portal_path = project_root / "config" / "portals" / f"{portal_name}.yaml"
        portals[portal_name] = load_portal_config(portal_path)

    # Initialize components
    http_client = HttpClient()
    
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "carhunter.db"
    
    repository = SqliteListingRepository(db_path)
    await repository.init_db()

    event_bus = EventBus()
    
    # Setup notifiers
    notifiers = []
    for notifier_name in settings.active_notifiers:
        notifier_class = NOTIFIERS_REGISTRY.get(notifier_name)
        if notifier_class:
            notifier = notifier_class()
            notifiers.append(notifier)
            event_bus.subscribe("new_listing", notifier.notify_new)
            event_bus.subscribe("price_drop", notifier.notify_price_drop)
        else:
            logging.error(f"Notifier {notifier_name} not found in registry")

    monitor_service = MonitorService(
        settings=settings,
        portals=portals,
        repository=repository,
        event_bus=event_bus,
        http_client=http_client
    )

    return monitor_service, http_client, repository

