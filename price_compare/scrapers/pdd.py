import random
import hashlib
from typing import List
from .base import BaseScraper
from ..models import Product

_BRANDS_PDD = [
    "小米", "华为", "Apple", "OPPO", "vivo", "三星", "荣耀", "一加", "realme", "iQOO",
    "戴尔", "惠普", "华硕", "联想", "机械革命", "雷神", "宏碁", "神舟", "清华同方", "海尔",
]

_MODEL_NAMES_PDD = [
    "Pro", "Max", "Ultra", "Lite", "SE", "Nova", "Mate",
    "Redmi", "Note", "Air", "Plus", "青春版", "尊享版",
    "X1", "S8", "15", "14", "16", "百亿补贴版", "特惠版",
]

_STORE_NAMES_PDD = [
    "品牌官方旗舰店", "百亿补贴专区", "品牌特卖店", "官方直营店",
    "品牌授权店", "工厂直供店", "品牌优选店", "官方旗舰店",
]

_TAGS_PDD = ["百亿补贴", "限时秒杀", "万人团", "品牌特卖", "全网最低", "正品险", "假一赔十", "拼团价"]

_PRODUCT_TEMPLATES = {
    "手机": ["{brand} {model} 5G手机 百亿补贴", "{brand} {model}正品手机", "{brand} {model}超值手机"],
    "笔记本": ["{brand} {model}笔记本 百亿补贴", "{brand} {model}高性能本", "{brand} {model}学生本"],
    "耳机": ["{brand} {model}蓝牙耳机 百亿补贴", "{brand} {model}无线耳机", "{brand} {model}降噪耳机"],
    "平板": ["{brand} {model}平板 百亿补贴", "{brand} {model}学习平板", "{brand} {model}网课平板"],
    "电视": ["{brand} {model}智能电视 百亿补贴", "{brand} {model}大屏电视", "{brand} {model}4K电视"],
    "洗衣机": ["{brand} {model}洗衣机 百亿补贴", "{brand} {model}全自动", "{brand} {model}洗烘一体"],
    "空调": ["{brand} {model}空调 百亿补贴", "{brand} {model}变频空调", "{brand} {model}节能空调"],
    "冰箱": ["{brand} {model}冰箱 百亿补贴", "{brand} {model}对开门", "{brand} {model}智能冰箱"],
    "默认": ["{brand} {model} 百亿补贴", "{brand} {model}超值好物", "{brand} {model}拼团价"],
}


class PDDScraper(BaseScraper):
    platform_name = "拼多多"
    base_url = "https://mobile.yangkeduo.com"

    def search(self, keyword: str, max_items: int = 20) -> List[Product]:
        random.seed(hashlib.md5(f"pdd_{keyword}".encode()).hexdigest())
        products = []
        category = self._detect_category(keyword)
        for i in range(min(max_items, random.randint(8, 20))):
            brand = random.choice(_BRANDS_PDD)
            model = random.choice(_MODEL_NAMES_PDD)
            template = random.choice(_PRODUCT_TEMPLATES.get(category, _PRODUCT_TEMPLATES["默认"]))
            name = template.format(brand=brand, model=model) + f" {keyword}"

            base_price = self._get_base_price(category)
            price = round(base_price * random.uniform(0.5, 1.15), 2)
            original_price = round(price * random.uniform(1.15, 1.6), 2) if random.random() > 0.2 else None
            sales = random.randint(200, 500000)
            store_rating = round(random.uniform(3.8, 4.9), 1)
            store = random.choice(_STORE_NAMES_PDD)
            tags = random.sample(_TAGS_PDD, k=random.randint(1, 3))

            goods_id = hashlib.md5(f"pdd_{keyword}_{i}".encode()).hexdigest()[:10]
            url = f"https://mobile.yangkeduo.com/goods.html?goods_id={goods_id}"

            products.append(Product(
                name=name,
                price=price,
                sales=sales,
                store_name=f"{brand}{store}",
                store_rating=store_rating,
                url=url,
                platform="拼多多",
                keyword=keyword,
                original_price=original_price,
                discount=f"-{round((1 - price / original_price) * 100)}%" if original_price else None,
                tags=tags,
            ))
        return products

    def get_product_detail(self, product_id: str) -> Product:
        products = self.search("默认", max_items=1)
        if products:
            p = products[0]
            p.product_id = product_id
            return p
        raise ValueError(f"Product {product_id} not found")

    def _detect_category(self, keyword: str) -> str:
        category_map = {
            "手机": "手机", "iPhone": "手机", "华为": "手机", "小米": "手机",
            "笔记本": "笔记本", "电脑": "笔记本",
            "耳机": "耳机", "AirPods": "耳机",
            "平板": "平板", "iPad": "平板",
            "电视": "电视", "洗衣机": "洗衣机", "空调": "空调", "冰箱": "冰箱",
        }
        for k, v in category_map.items():
            if k in keyword:
                return v
        return "默认"

    def _get_base_price(self, category: str) -> float:
        price_map = {
            "手机": 2500, "笔记本": 4000, "耳机": 200,
            "平板": 2000, "电视": 2500, "洗衣机": 1500,
            "空调": 2000, "冰箱": 2000, "默认": 350,
        }
        return price_map.get(category, 350)
