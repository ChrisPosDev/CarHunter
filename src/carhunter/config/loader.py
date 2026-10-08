import yaml
from pathlib import Path
from .schema import Settings, PortalConfig

def load_settings(path: str | Path) -> Settings:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Settings(**data)

def load_portal_config(path: str | Path) -> PortalConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return PortalConfig(**data)

