from .base import BaseScraper
from .jd import JDScraper
from .taobao import TaobaoScraper
from .pdd import PDDScraper

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "jd": JDScraper,
    "taobao": TaobaoScraper,
    "pdd": PDDScraper,
}


def get_scraper(platform: str) -> BaseScraper:
    cls = SCRAPER_REGISTRY.get(platform.lower())
    if not cls:
        raise ValueError(f"Unknown platform: {platform}. Available: {list(SCRAPER_REGISTRY.keys())}")
    return cls()


def get_all_scrapers() -> list[BaseScraper]:
    return [cls() for cls in SCRAPER_REGISTRY.values()]


__all__ = ["BaseScraper", "JDScraper", "TaobaoScraper", "PDDScraper", "SCRAPER_REGISTRY", "get_scraper", "get_all_scrapers"]
