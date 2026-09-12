from typing import Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.modules.inventory.infrastructure.models import Inventory
from app.modules.products.infrastructure.models import Product
from app.modules.sales.infrastructure.models import SaleItem, Sale, SaleStatus


def analyze_sales_anomalies(db: Session) -> list[dict[str, Any]]:
    """Analyze products for sales anomalies (e.g. zero sales for high-velocity items or sudden sales spikes)."""
    inventories = db.execute(
        select(Inventory, Product).join(Product, Inventory.product_id == Product.id)
    ).all()

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

    anomalies = []
    for inv, prod in inventories:
        total_sold = sales_map.get(prod.id, 0.0)
        total_stock = inv.display_quantity + inv.on_hand_quantity

        # Anomaly case 1: High stock, zero sales
        if total_stock >= 50 and total_sold == 0:
            anomalies.append({
                "product_id": str(prod.id),
                "gtin": prod.gtin,
                "name": prod.name,
                "anomaly_type": "DEAD_STOCK",
                "severity": "WARNING",
                "description": f"Stok melimpah ({total_stock} unit) tetapi belum ada penjualan tercatat.",
                "recommended_action": "Pertimbangkan diskon / penataan ulang posisi display produk."
            })
        # Anomaly case 2: Stock is on hand but display stock is zero
        elif inv.display_quantity == 0 and inv.on_hand_quantity > 10:
            anomalies.append({
                "product_id": str(prod.id),
                "gtin": prod.gtin,
                "name": prod.name,
                "anomaly_type": "UNSHELVED_STOCK",
                "severity": "CRITICAL",
                "description": f"Stok di rak display KOSONG, padahal di gudang (On-Hand) tersisa {inv.on_hand_quantity} unit.",
                "recommended_action": "Lakukan transfer display segera agar barang dapat dibeli konsumen."
            })

    return anomalies
