from typing import Any
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.inventory.infrastructure.models import Inventory
from app.modules.products.infrastructure.models import Product
from app.modules.suppliers.infrastructure.models import SupplierProduct, Supplier
from app.modules.sales.infrastructure.models import SaleItem, Sale, SaleStatus


def generate_reorder_recommendations(db: Session, product_id: str | None = None) -> list[dict[str, Any]]:
    """Generate actionable reorder recommendations including recommended order quantity and primary supplier info."""
    stmt = select(Inventory, Product).join(Product, Inventory.product_id == Product.id)
    if product_id:
        stmt = stmt.where(Product.id == UUID(product_id))

    inventories = db.execute(stmt).all()

    sales_stmt = (
        select(
            SaleItem.product_id,
            func.sum(SaleItem.quantity).label("total_sold")
        )
        .join(Sale, SaleItem.sale_id == Sale.id)
        .where(Sale.status == SaleStatus.COMPLETED)
        .group_by(SaleItem.product_id)
    )
    sales_map = {row.product_id: float(row.total_sold or 0) for row in db.execute(sales_stmt).all()}

    recommendations = []
    for inv, prod in inventories:
        total_stock = inv.display_quantity + inv.on_hand_quantity
        total_sold = sales_map.get(prod.id, 0.0)
        daily_burn_rate = round(total_sold / 14.0, 2) if total_sold > 0 else 0.5
        min_stock = getattr(prod, "minimum_stock_alert", 10)

        # Recommend reorder if total stock is below min_stock or days_left <= 7
        days_left = round(total_stock / daily_burn_rate, 1) if daily_burn_rate > 0 else 999.0

        if total_stock <= min_stock or days_left <= 7:
            # Query linked supplier
            sp_stmt = (
                select(SupplierProduct, Supplier)
                .join(Supplier, SupplierProduct.supplier_id == Supplier.id)
                .where(SupplierProduct.product_id == prod.id)
                .limit(1)
            )
            sp_row = db.execute(sp_stmt).first()
            supplier_name = sp_row[1].name if sp_row else "Supplier Umum"

            recommended_qty = max(24, int(daily_burn_rate * 14))

            recommendations.append({
                "product_id": str(prod.id),
                "gtin": prod.gtin,
                "name": prod.name,
                "current_stock": total_stock,
                "days_left": days_left,
                "recommended_reorder_qty": recommended_qty,
                "primary_supplier": supplier_name,
                "reason": f"Stok tersisa {total_stock} unit (Batas min: {min_stock}). Estimasi habis dalam {days_left} hari."
            })

    return recommendations
