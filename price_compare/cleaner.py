from typing import List, Dict, Optional
from .models import Product
from difflib import SequenceMatcher


class DataCleaner:
    def __init__(self, similarity_threshold: float = 0.75):
        self.similarity_threshold = similarity_threshold

    def clean(self, products: List[Product]) -> List[Product]:
        products = self._remove_invalid(products)
        products = self._normalize_prices(products)
        products = self._deduplicate(products)
        products = self._sort_by_price(products)
        return products

    def _remove_invalid(self, products: List[Product]) -> List[Product]:
        valid = []
        for p in products:
            if p.price <= 0:
                continue
            if not p.name or len(p.name.strip()) < 2:
                continue
            if not p.url:
                continue
            valid.append(p)
        return valid

    def _normalize_prices(self, products: List[Product]) -> List[Product]:
        for p in products:
            p.price = round(p.price, 2)
            if p.original_price and p.original_price < p.price:
                p.original_price = None
                p.discount = None
        return products

    def _deduplicate(self, products: List[Product]) -> List[Product]:
        seen_urls = set()
        unique = []
        for p in products:
            if p.url in seen_urls:
                continue
            seen_urls.add(p.url)

            is_duplicate = False
            for existing in unique:
                if (p.platform == existing.platform and
                        self._name_similarity(p.name, existing.name) > self.similarity_threshold and
                        abs(p.price - existing.price) / max(p.price, existing.price) < 0.05):
                    if p.sales > existing.sales:
                        idx = unique.index(existing)
                        unique[idx] = p
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(p)

        return unique

    def _sort_by_price(self, products: List[Product]) -> List[Product]:
        return sorted(products, key=lambda p: p.price)

    @staticmethod
    def _name_similarity(name1: str, name2: str) -> float:
        return SequenceMatcher(None, name1, name2).ratio()

    @staticmethod
    def get_statistics(products: List[Product]) -> Dict:
        if not products:
            return {}
        prices = [p.price for p in products]
        sales = [p.sales for p in products]
        ratings = [p.store_rating for p in products]
        platforms = {}
        for p in products:
            platforms[p.platform] = platforms.get(p.platform, 0) + 1

        return {
            "total": len(products),
            "price_min": min(prices),
            "price_max": max(prices),
            "price_avg": round(sum(prices) / len(prices), 2),
            "price_median": sorted(prices)[len(prices) // 2],
            "sales_total": sum(sales),
            "sales_avg": round(sum(sales) / len(sales)),
            "rating_avg": round(sum(ratings) / len(ratings), 1),
            "platforms": platforms,
        }
