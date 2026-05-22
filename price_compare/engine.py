from typing import List, Dict, Optional
from .models import Product
from .scrapers import get_all_scrapers, get_scraper, BaseScraper
from .cleaner import DataCleaner
from .comparator import ProductComparator
from .visualizer import Visualizer


_PLATFORM_ALIASES = {"京东": "jd", "淘宝": "taobao", "拼多多": "pdd"}


class PriceCompareEngine:
    def __init__(self, platforms: Optional[List[str]] = None):
        if platforms:
            resolved = [self._resolve_platform(p) for p in platforms]
            self.scrapers = [get_scraper(p) for p in resolved]
        else:
            self.scrapers = get_all_scrapers()
        self.cleaner = DataCleaner()
        self.comparator = ProductComparator()
        self.visualizer = Visualizer()

    @staticmethod
    def _resolve_platform(name: str) -> str:
        return _PLATFORM_ALIASES.get(name, name)

    def search(self, keyword: str, max_items_per_platform: int = 20) -> Dict:
        raw_products = []
        for scraper in self.scrapers:
            try:
                products = scraper.search(keyword, max_items=max_items_per_platform)
                raw_products.extend(products)
            except Exception as e:
                print(f"  ⚠ {scraper.platform_name} 采集失败: {e}")

        cleaned = self.cleaner.clean(raw_products)
        comparison = self.comparator.compare(cleaned)
        chart_data = self.visualizer.generate_chart_data(cleaned, comparison)

        stats = self.cleaner.get_statistics(cleaned)

        return {
            "keyword": keyword,
            "raw_count": len(raw_products),
            "cleaned_count": len(cleaned),
            "products": cleaned,
            "comparison": comparison,
            "chart_data": chart_data,
            "statistics": stats,
        }

    def search_to_json(self, keyword: str, output_path: str, max_items_per_platform: int = 20) -> str:
        result = self.search(keyword, max_items_per_platform)
        return self.visualizer.export_json(
            result["products"],
            result["comparison"],
            result["chart_data"],
            output_path,
        )

    def search_to_report(self, keyword: str, max_items_per_platform: int = 20) -> str:
        result = self.search(keyword, max_items_per_platform)
        return self.visualizer.generate_cli_report(result["products"], result["comparison"])
