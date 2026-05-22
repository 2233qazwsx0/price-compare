from abc import ABC, abstractmethod
from typing import List
from ..models import Product


class BaseScraper(ABC):
    platform_name: str = ""
    base_url: str = ""

    @abstractmethod
    def search(self, keyword: str, max_items: int = 20) -> List[Product]:
        raise NotImplementedError

    @abstractmethod
    def get_product_detail(self, product_id: str) -> Product:
        raise NotImplementedError

    def _build_url(self, keyword: str) -> str:
        return f"{self.base_url}/search?q={keyword}"

    def __repr__(self):
        return f"<{self.__class__.__name__} platform={self.platform_name}>"
