from typing import Any
from sqlalchemy.orm import Session
from app.infrastructure.product_provider.base import ProductProvider
from app.modules.products.infrastructure.models import Product


class DatabaseProductProvider(ProductProvider):
    """Product Provider implementation querying the local PostgreSQL master catalog."""

    def __init__(self, db: Session):
        self.db = db

    def get_product_by_gtin(self, gtin: str) -> dict[str, Any] | None:
        product = self.db.query(Product).filter(Product.gtin == gtin).first()
        if not product:
            return None
        return {
            "id": str(product.id),
            "gtin": product.gtin,
            "name": product.name,
            "brand": product.brand,
            "category_id": str(product.category_id) if product.category_id else None,
            "unit": product.unit,
            "purchase_price": float(product.purchase_price),
            "selling_price": float(product.selling_price),
            "status": product.status.value if hasattr(product.status, "value") else str(product.status),
        }

    def search_products(self, query: str) -> list[dict[str, Any]]:
        search_pattern = f"%{query}%"
        products = (
            self.db.query(Product)
            .filter((Product.name.ilike(search_pattern)) | (Product.gtin.ilike(search_pattern)))
            .limit(20)
            .all()
        )
        return [
            {
                "id": str(p.id),
                "gtin": p.gtin,
                "name": p.name,
                "brand": p.brand,
                "category_id": str(p.category_id) if p.category_id else None,
                "unit": p.unit,
                "purchase_price": float(p.purchase_price),
                "selling_price": float(p.selling_price),
                "status": p.status.value if hasattr(p.status, "value") else str(p.status),
            }
            for p in products
        ]
