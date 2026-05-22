from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class Product:
    name: str
    price: float
    sales: int
    store_name: str
    store_rating: float
    url: str
    platform: str
    keyword: str = ""
    product_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    image_url: str = ""
    original_price: Optional[float] = None
    discount: Optional[str] = None
    tags: list = field(default_factory=list)
    collected_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @property
    def price_per_sale(self) -> float:
        if self.sales == 0:
            return float("inf")
        return self.price

    @property
    def value_score(self) -> float:
        rating_factor = self.store_rating / 5.0 if self.store_rating > 0 else 0.5
        sales_factor = min(self.sales / 10000, 1.0) if self.sales > 0 else 0.01
        price_factor = 1.0
        if self.original_price and self.original_price > 0:
            price_factor = self.price / self.original_price
        return round(rating_factor * 0.3 + sales_factor * 0.4 + (1 - price_factor) * 0.3, 3)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["value_score"] = self.value_score
        d["price_per_sale"] = self.price_per_sale
        return d
