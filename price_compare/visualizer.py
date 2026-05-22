import json
import os
from typing import List, Dict, Optional
from .models import Product
from .comparator import ProductComparator


class Visualizer:
    PLATFORM_COLORS = {
        "京东": "#E4393C",
        "淘宝": "#FF6A00",
        "拼多多": "#E02E24",
    }

    def generate_chart_data(self, products: List[Product], comparison: Dict) -> Dict:
        return {
            "price_bar": self._price_bar_data(products),
            "platform_comparison": self._platform_comparison_data(comparison),
            "price_distribution": self._price_distribution_data(comparison),
            "value_scatter": self._value_scatter_data(products),
            "sales_ranking": self._sales_ranking_data(products),
            "price_trend": self._price_trend_data(products),
        }

    def _price_bar_data(self, products: List[Product]) -> Dict:
        sorted_products = sorted(products, key=lambda p: p.price)[:20]
        return {
            "labels": [f"{p.name[:15]}..." if len(p.name) > 15 else p.name for p in sorted_products],
            "prices": [p.price for p in sorted_products],
            "original_prices": [p.original_price for p in sorted_products],
            "platforms": [p.platform for p in sorted_products],
            "colors": [self.PLATFORM_COLORS.get(p.platform, "#999") for p in sorted_products],
        }

    def _platform_comparison_data(self, comparison: Dict) -> Dict:
        platform_data = comparison.get("platform_comparison", {})
        if not platform_data:
            return {"labels": [], "avg_prices": [], "min_prices": [], "avg_ratings": [], "colors": []}
        labels = list(platform_data.keys())
        return {
            "labels": labels,
            "avg_prices": [platform_data[l]["avg_price"] for l in labels],
            "min_prices": [platform_data[l]["min_price"] for l in labels],
            "avg_ratings": [platform_data[l]["avg_rating"] for l in labels],
            "colors": [self.PLATFORM_COLORS.get(l, "#999") for l in labels],
        }

    def _price_distribution_data(self, comparison: Dict) -> Dict:
        analysis = comparison.get("price_analysis", {})
        buckets = analysis.get("buckets", {})
        return {
            "labels": list(buckets.keys()),
            "counts": list(buckets.values()),
            "stats": {k: v for k, v in analysis.items() if k != "buckets"},
        }

    def _value_scatter_data(self, products: List[Product]) -> Dict:
        datasets = {}
        for p in products:
            if p.platform not in datasets:
                datasets[p.platform] = {"points": [], "names": []}
            datasets[p.platform]["points"].append({
                "x": p.price,
                "y": p.value_score,
                "r": max(4, min(15, p.sales / 20000)),
            })
            datasets[p.platform]["names"].append(p.name[:20])

        result = {}
        for platform, data in datasets.items():
            result[platform] = {
                "points": data["points"],
                "names": data["names"],
                "color": self.PLATFORM_COLORS.get(platform, "#999"),
            }
        return result

    def _sales_ranking_data(self, products: List[Product]) -> Dict:
        top10 = sorted(products, key=lambda p: p.sales, reverse=True)[:10]
        return {
            "labels": [f"{p.name[:15]}..." if len(p.name) > 15 else p.name for p in top10],
            "sales": [p.sales for p in top10],
            "platforms": [p.platform for p in top10],
            "colors": [self.PLATFORM_COLORS.get(p.platform, "#999") for p in top10],
        }

    def _price_trend_data(self, products: List[Product]) -> Dict:
        import random
        from datetime import datetime, timedelta

        platforms = {}
        for p in products:
            if p.platform not in platforms:
                platforms[p.platform] = []
            platforms[p.platform].append(p.price)

        now = datetime.now()
        dates = [(now - timedelta(days=30 - i)).strftime("%m-%d") for i in range(30)]

        result = {}
        for platform, prices in platforms.items():
            avg_price = sum(prices) / len(prices)
            trend = []
            for i in range(30):
                variation = random.uniform(-0.08, 0.08)
                trend.append(round(avg_price * (1 + variation), 2))
            result[platform] = {
                "dates": dates,
                "prices": trend,
                "color": self.PLATFORM_COLORS.get(platform, "#999"),
            }

        return result

    def export_json(self, products: List[Product], comparison: Dict, chart_data: Dict, output_path: str) -> str:
        output = {
            "products": [p.to_dict() for p in products],
            "comparison": comparison,
            "charts": chart_data,
        }
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        return output_path

    def generate_cli_report(self, products: List[Product], comparison: Dict) -> str:
        lines = []
        lines.append("=" * 80)
        lines.append("  电商商品价格对比报告")
        lines.append("=" * 80)

        stats = comparison.get("price_analysis", {})
        if stats:
            lines.append(f"\n  📊 价格统计: 最低 ¥{stats.get('min', 0)} | "
                         f"中位数 ¥{stats.get('median', 0)} | "
                         f"最高 ¥{stats.get('max', 0)}")

        recs = comparison.get("recommendations", {})
        if recs:
            lines.append("\n" + "─" * 80)
            lines.append("  ⭐ 性价比推荐")
            lines.append("─" * 80)
            best = recs.get("best_value")
            if best:
                lines.append(f"  🏆 最佳性价比: {best['name']}")
                lines.append(f"     平台: {best['platform']} | 价格: ¥{best['price']} | "
                             f"评分: {best['store_rating']} | 销量: {best['sales']:,}")
            cheapest = recs.get("lowest_price")
            if cheapest:
                lines.append(f"  💰 最低价格: {cheapest['name']}")
                lines.append(f"     平台: {cheapest['platform']} | 价格: ¥{cheapest['price']} | "
                             f"评分: {cheapest['store_rating']} | 销量: {cheapest['sales']:,}")
            popular = recs.get("highest_sales")
            if popular:
                lines.append(f"  🔥 最高销量: {popular['name']}")
                lines.append(f"     平台: {popular['platform']} | 价格: ¥{popular['price']} | "
                             f"评分: {popular['store_rating']} | 销量: {popular['sales']:,}")

        lines.append("\n" + "─" * 80)
        lines.append("  📋 商品列表 (按价格从低到高)")
        lines.append("─" * 80)
        lines.append(f"  {'序号':<4} {'平台':<6} {'价格':<10} {'原价':<10} {'销量':<10} {'评分':<5} {'商品名称'}")
        lines.append("  " + "-" * 76)

        comp_list = comparison.get("comparison", [])
        for i, item in enumerate(comp_list[:30], 1):
            orig = f"¥{item['original_price']}" if item.get("original_price") else "-"
            discount = item.get("discount") or ""
            name = item["name"][:30] + "..." if len(item["name"]) > 30 else item["name"]
            discount_str = f" {discount}" if discount else ""
            lines.append(f"  {i:<4} {item['platform']:<6} ¥{item['price']:<9} {orig:<10} "
                         f"{item['sales']:<10,} {item['store_rating']:<5} {name}{discount_str}")

        platform_comp = comparison.get("platform_comparison", {})
        if platform_comp:
            lines.append("\n" + "─" * 80)
            lines.append("  🏪 平台对比")
            lines.append("─" * 80)
            for name, data in platform_comp.items():
                lines.append(f"  {name}: 均价 ¥{data['avg_price']} | 最低 ¥{data['min_price']} | "
                             f"最高 ¥{data['max_price']} | 均销 {data['avg_sales']:,} | 均分 {data['avg_rating']}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)
