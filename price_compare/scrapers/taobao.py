import random
import hashlib
from typing import List
from .base import BaseScraper
from ..models import Product

_BRANDS_TB = [
    "小米", "华为", "Apple", "OPPO", "vivo", "三星", "荣耀", "一加", "魅族", "努比亚",
    "戴尔", "惠普", "华硕", "ThinkPad", "机械革命", "雷神", "宏碁", "微星", "神舟", "清华同方",
]

_MODEL_NAMES_TB = [
    "Pro", "Max", "Ultra", "Lite", "SE", "Nova", "Mate", "Reno",
    "Galaxy", "Redmi", "Note", "Air", "Book", "Plus", "Elite",
    "X1", "S8", "15", "14", "16", "Z7", "V3", "青春版", "尊享版", "典藏版",
]

_STORE_NAMES_TB = [
    "品牌旗舰店", "官方旗舰店", "品牌专卖店", "天猫旗舰店",
    "品牌直营店", "官方授权店", "品牌体验店", "天猫直营店",
]

_TAGS_TB = ["天猫好物", "跨店满减", "88VIP价", "新品上市", "热销爆款", "限时折扣", "品牌特卖", "聚划算"]

_PRODUCT_TEMPLATES = {
    "手机": ["{brand} {model} 5G全网通手机", "{brand} {model}拍照旗舰", "{brand} {model}超长续航"],
    "笔记本": ["{brand} {model}超薄本", "{brand} {model}游戏性能本", "{brand} {model}设计师本"],
    "耳机": ["{brand} {model}真无线耳机", "{brand} {model}主动降噪", "{brand} {model}运动耳机"],
    "平板": ["{brand} {model}高清平板", "{brand} {model}网课平板", "{brand} {model}影音平板"],
    "电视": ["{brand} {model}智慧屏", "{brand} {model}HDR电视", "{brand} {model}护眼电视"],
    "洗衣机": ["{brand} {model}洗烘套装", "{brand} {model}变频洗衣机", "{brand} {model}迷你洗衣机"],
    "空调": ["{brand} {model}一级能效", "{brand} {model}静音空调", "{brand} {model}智能空调"],
    "冰箱": ["{brand} {model}风冷冰箱", "{brand} {model}多门冰箱", "{brand} {model}小型冰箱"],
}


class TaobaoScraper(BaseScraper):
    platform_name = "淘宝"
    base_url = "https://s.taobao.com"

    def search(self, keyword: str, max_items: int = 20) -> List[Product]:
        random.seed(hashlib.md5(f"tb_{keyword}".encode()).hexdigest())
        products = []
        category = self._detect_category(keyword)
        has_category = category is not None and category in _PRODUCT_TEMPLATES
        for i in range(min(max_items, random.randint(8, 20))):
            brand = random.choice(_BRANDS_TB)
            if has_category:
                model = random.choice(_MODEL_NAMES_TB)
                template = random.choice(_PRODUCT_TEMPLATES[category])
                name = template.format(brand=brand, model=model)
            else:
                suffixes = ["高性能版", "标准版", "旗舰版", "入门版", "增强版", "专业版", "经典版", "升级版"]
                name = f"{brand} {random.choice(suffixes)} {keyword}"

            base_price = self._get_base_price(category)
            price = round(base_price * random.uniform(0.6, 1.25), 2)
            original_price = round(price * random.uniform(1.1, 1.5), 2) if random.random() > 0.4 else None
            sales = random.randint(50, 300000)
            store_rating = round(random.uniform(4.0, 5.0), 1)
            store = random.choice(_STORE_NAMES_TB)
            tags = random.sample(_TAGS_TB, k=random.randint(1, 3))

            item_id = hashlib.md5(f"tb_{keyword}_{i}".encode()).hexdigest()[:12]
            url = f"https://item.taobao.com/item.htm?id={item_id}"

            products.append(Product(
                name=name,
                price=price,
                sales=sales,
                store_name=f"{brand}{store}",
                store_rating=store_rating,
                url=url,
                platform="淘宝",
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

    def _detect_category(self, keyword: str) -> Optional[str]:
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
        return None

    def _get_base_price(self, category: Optional[str]) -> float:
        price_map = {
            "手机": 2800, "笔记本": 4500, "耳机": 250,
            "平板": 2200, "电视": 2800, "洗衣机": 1800,
            "空调": 2200, "冰箱": 2200,
        }
        if category and category in price_map:
            return price_map[category]
        # 通用价格区间
        return random.randint(100, 2000)
