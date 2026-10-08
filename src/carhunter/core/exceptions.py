class CarHunterError(Exception):
    """Base exception for all CarHunter errors."""


class ConfigError(CarHunterError):
    """Raised when configuration is invalid or missing."""


class StrategyError(CarHunterError):
    """Raised when a scraping strategy fails to extract data."""


class FetchError(CarHunterError):
    """Raised when HTTP request fails."""

