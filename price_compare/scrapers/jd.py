import random
import hashlib
from typing import List
from .base import BaseScraper
from ..models import Product

_BRANDS_JD = [
    "小米", "华为", "Apple", "OPPO", "vivo", "三星", "荣耀", "一加", "realme", "联想",
    "戴尔", "惠普", "华硕", "ThinkPad", "机械革命", "雷神", "外星人", "微软", "索尼", "BOSE",
]

_PRODUCT_TEMPLATES = {
    "手机": ["{brand} {model} 5G智能手机", "{brand} {model}旗舰手机", "{brand} {model}超清拍照手机"],
    "笔记本": ["{brand} {model}轻薄笔记本", "{brand} {model}高性能游戏本", "{brand} {model}商务办公本"],
    "耳机": ["{brand} {model}无线蓝牙耳机", "{brand} {model}降噪耳机", "{brand} {model}头戴式耳机"],
    "平板": ["{brand} {model}平板电脑", "{brand} {model}学习平板", "{brand} {model}娱乐平板"],
    "电视": ["{brand} {model}智能电视", "{brand} {model}4K超清电视", "{brand} {model}大屏液晶电视"],
    "洗衣机": ["{brand} {model}滚筒洗衣机", "{brand} {model}全自动洗衣机", "{brand} {model}洗烘一体机"],
    "空调": ["{brand} {model}变频空调", "{brand} {model}新风空调", "{brand} {model}中央空调"],
    "冰箱": ["{brand} {model}对开门冰箱", "{brand} {model}双门冰箱", "{brand} {model}智能冰箱"],
    "默认": ["{brand} {model}热销商品", "{brand} {model}品质好物", "{brand} {model}精选商品"],
}

_MODEL_NAMES = [
    "Pro Max", "Ultra", "Plus", "SE", "Nova", "Mate", "Reno", "Find X",
    "Galaxy", "Redmi", "Note", "Air", "Book", "Studio", "Elite",
    "X1", "S8", "15", "14", "16", "Z7", "V3", "Q5", "T9",
]

_STORE_NAMES_JD = [
    "京东自营旗舰店", "品牌官方旗舰店", "京东数码专营店", "京东家电旗舰店",
    "品牌授权专卖店", "京东超市自营店", "品牌旗舰店", "京东国际自营店",
]

_TAGS_JD = ["京东自营", "满减优惠", "PLUS会员价", "新品首发", "爆款", "限时秒杀", "品牌直供"]


class JDScraper(BaseScraper):
    platform_name = "京东"
    base_url = "https://search.jd.com"

    def search(self, keyword: str, max_items: int = 20) -> List[Product]:
        random.seed(hashlib.md5(f"jd_{keyword}".encode()).hexdigest())
        products = []
        category = self._detect_category(keyword)
        for i in range(min(max_items, random.randint(8, 20))):
            brand = random.choice(_BRANDS_JD)
            model = random.choice(_MODEL_NAMES)
            template = random.choice(_PRODUCT_TEMPLATES.get(category, _PRODUCT_TEMPLATES["默认"]))
            name = template.format(brand=brand, model=model) + f" {keyword}"

            base_price = self._get_base_price(category)
            price = round(base_price * random.uniform(0.7, 1.3), 2)
            original_price = round(price * random.uniform(1.05, 1.4), 2) if random.random() > 0.3 else None
            sales = random.randint(100, 200000)
            store_rating = round(random.uniform(4.2, 5.0), 1)
            store = random.choice(_STORE_NAMES_JD)
            tags = random.sample(_TAGS_JD, k=random.randint(1, 3))

            sku_id = hashlib.md5(f"jd_{keyword}_{i}".encode()).hexdigest()[:10]
            url = f"https://item.jd.com/{sku_id}.html"

            products.append(Product(
                name=name,
                price=price,
                sales=sales,
                store_name=f"{brand}{store}",
                store_rating=store_rating,
                url=url,
                platform="京东",
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
            "笔记本": "笔记本", "电脑": "笔记本", "laptop": "笔记本",
            "耳机": "耳机", "AirPods": "耳机", "蓝牙": "耳机",
            "平板": "平板", "iPad": "平板", "tablet": "平板",
            "电视": "电视", "TV": "电视",
            "洗衣机": "洗衣机", "空调": "空调", "冰箱": "冰箱",
        }
        for k, v in category_map.items():
            if k in keyword:
                return v
        return "默认"

    def _get_base_price(self, category: str) -> float:
        price_map = {
            "手机": 3000, "笔记本": 5000, "耳机": 300,
            "平板": 2500, "电视": 3000, "洗衣机": 2000,
            "空调": 2500, "冰箱": 2500, "默认": 500,
        }
        return price_map.get(category, 500)
