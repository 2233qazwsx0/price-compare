from typing import List, Dict, Tuple
from .models import Product


class ProductComparator:
    def compare(self, products: List[Product]) -> Dict:
        if not products:
            return {"comparison": [], "recommendations": {}, "price_analysis": {}}

        comparison = self._build_comparison(products)
        recommendations = self._get_recommendations(products)
        price_analysis = self._analyze_price_distribution(products)
        platform_comparison = self._compare_platforms(products)

        return {
            "comparison": comparison,
            "recommendations": recommendations,
            "price_analysis": price_analysis,
            "platform_comparison": platform_comparison,
        }

    def _build_comparison(self, products: List[Product]) -> List[Dict]:
        comparison = []
        price_min = min(p.price for p in products)
        price_max = max(p.price for p in products)
        price_range = price_max - price_min if price_max > price_min else 1

        for p in products:
            price_score = round((1 - (p.price - price_min) / price_range) * 100, 1)
            rating_score = round((p.store_rating / 5.0) * 100, 1)
            sales_score = round(min(p.sales / max(pp.sales for pp in products), 1.0) * 100, 1)
            value_score = round(p.value_score * 100, 1)

            comparison.append({
                "product_id": p.product_id,
                "name": p.name,
                "platform": p.platform,
                "price": p.price,
                "original_price": p.original_price,
                "discount": p.discount,
                "sales": p.sales,
                "store_name": p.store_name,
                "store_rating": p.store_rating,
                "url": p.url,
                "tags": p.tags,
                "scores": {
                    "price_score": price_score,
                    "rating_score": rating_score,
                    "sales_score": sales_score,
                    "value_score": value_score,
                },
            })

        comparison.sort(key=lambda x: x["scores"]["value_score"], reverse=True)
        return comparison

    def _get_recommendations(self, products: List[Product]) -> Dict:
        by_value = sorted(products, key=lambda p: p.value_score, reverse=True)
        by_price = sorted(products, key=lambda p: p.price)
        by_sales = sorted(products, key=lambda p: p.sales, reverse=True)
        by_rating = sorted(products, key=lambda p: p.store_rating, reverse=True)

        return {
            "best_value": by_value[0].to_dict() if by_value else None,
            "lowest_price": by_price[0].to_dict() if by_price else None,
            "highest_sales": by_sales[0].to_dict() if by_sales else None,
            "best_rating": by_rating[0].to_dict() if by_rating else None,
            "top3_value": [p.to_dict() for p in by_value[:3]],
        }

    def _analyze_price_distribution(self, products: List[Product]) -> Dict:
        prices = sorted([p.price for p in products])
        if not prices:
            return {}

        n = len(prices)
        q1 = prices[n // 4] if n >= 4 else prices[0]
        q2 = prices[n // 2]
        q3 = prices[3 * n // 4] if n >= 4 else prices[-1]

        buckets = {}
        bucket_size = max((prices[-1] - prices[0]) / 5, 1)
        for p in products:
            bucket_idx = int((p.price - prices[0]) / bucket_size)
            bucket_idx = min(bucket_idx, 4)
            bucket_label = f"{round(prices[0] + bucket_idx * bucket_size)}-{round(prices[0] + (bucket_idx + 1) * bucket_size)}"
            buckets[bucket_label] = buckets.get(bucket_label, 0) + 1

        return {
            "min": prices[0],
            "q1": q1,
            "median": q2,
            "q3": q3,
            "max": prices[-1],
            "buckets": buckets,
        }

    def _compare_platforms(self, products: List[Product]) -> Dict:
        platforms = {}
        for p in products:
            if p.platform not in platforms:
                platforms[p.platform] = {"prices": [], "sales": [], "ratings": [], "count": 0}
            platforms[p.platform]["prices"].append(p.price)
            platforms[p.platform]["sales"].append(p.sales)
            platforms[p.platform]["ratings"].append(p.store_rating)
            platforms[p.platform]["count"] += 1

        result = {}
        for name, data in platforms.items():
            result[name] = {
                "count": data["count"],
                "avg_price": round(sum(data["prices"]) / len(data["prices"]), 2),
                "min_price": min(data["prices"]),
                "max_price": max(data["prices"]),
                "avg_sales": round(sum(data["sales"]) / len(data["sales"])),
                "avg_rating": round(sum(data["ratings"]) / len(data["ratings"]), 1),
            }

        return result
