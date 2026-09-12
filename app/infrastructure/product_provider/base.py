from abc import ABC, abstractmethod
from typing import Any


class ProductProvider(ABC):
    """Abstract interface for product data provider (GS1, CSV catalog, local DB)."""

    @abstractmethod
    def get_product_by_gtin(self, gtin: str) -> dict[str, Any] | None:
        """Lookup product info by GTIN / EAN-13."""
        pass

    @abstractmethod
    def search_products(self, query: str) -> list[dict[str, Any]]:
        """Search products in provider catalog by query string."""
        pass
