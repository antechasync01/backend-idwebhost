import uuid
from datetime import datetime
from sqlalchemy import cast, Date, desc, func, select
from sqlalchemy.orm import Session

from app.modules.inventory.infrastructure.models import Inventory
from app.modules.products.infrastructure.models import Product
from app.modules.sales.infrastructure.models import Sale, SaleItem, SaleRefund, SaleStatus


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_sales_summary(self, start_date: datetime, end_date: datetime) -> dict:
        """Calculate gross revenue, refunds, net revenue, transaction count, avg transaction value, and items sold."""
        # 1. Gross revenue & sales count
        sales_query = (
            self.db.query(
                func.coalesce(func.sum(Sale.total_amount), 0.0).label("gross_revenue"),
                func.count(Sale.id).label("transaction_count"),
            )
            .filter(
                Sale.status == SaleStatus.COMPLETED,
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
            )
            .first()
        )

        gross_revenue = float(sales_query.gross_revenue) if sales_query else 0.0
        transaction_count = int(sales_query.transaction_count) if sales_query else 0

        # 2. Total Refunds
        refunds_query = (
            self.db.query(func.coalesce(func.sum(SaleRefund.refund_amount), 0.0))
            .filter(
                SaleRefund.created_at >= start_date,
                SaleRefund.created_at <= end_date,
            )
            .scalar()
        )
        total_refunds = float(refunds_query) if refunds_query else 0.0

        # 3. Total Items Sold
        items_query = (
            self.db.query(func.coalesce(func.sum(SaleItem.quantity), 0))
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(
                Sale.status == SaleStatus.COMPLETED,
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
            )
            .scalar()
        )
        total_items_sold = int(items_query) if items_query else 0

        net_revenue = gross_revenue - total_refunds
        avg_transaction_value = gross_revenue / transaction_count if transaction_count > 0 else 0.0

        return {
            "gross_revenue": round(gross_revenue, 2),
            "total_refunds": round(total_refunds, 2),
            "net_revenue": round(net_revenue, 2),
            "transaction_count": transaction_count,
            "average_transaction_value": round(avg_transaction_value, 2),
            "total_items_sold": total_items_sold,
        }

    def get_top_selling_products(
        self, start_date: datetime, end_date: datetime, limit: int = 10
    ) -> list[dict]:
        """Fetch top products by quantity sold within date range."""
        results = (
            self.db.query(
                Product.id.label("product_id"),
                Product.gtin,
                Product.name.label("product_name"),
                func.sum(SaleItem.quantity).label("quantity_sold"),
                func.sum(SaleItem.subtotal).label("total_revenue"),
            )
            .join(SaleItem, SaleItem.product_id == Product.id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .filter(
                Sale.status == SaleStatus.COMPLETED,
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
            )
            .group_by(Product.id, Product.gtin, Product.name)
            .order_by(desc("quantity_sold"))
            .limit(limit)
            .all()
        )

        return [
            {
                "product_id": r.product_id,
                "gtin": r.gtin,
                "product_name": r.product_name,
                "quantity_sold": int(r.quantity_sold or 0),
                "total_revenue": round(float(r.total_revenue or 0.0), 2),
            }
            for r in results
        ]

    def get_inventory_health(self, low_stock_threshold: int = 10) -> dict:
        """Calculate total inventory metrics, stock valuation, and low/out-of-stock counts."""
        products = (
            self.db.query(
                Product,
                Inventory.display_quantity,
                Inventory.on_hand_quantity,
            )
            .join(Inventory, Inventory.product_id == Product.id)
            .all()
        )

        total_products = len(products)
        total_display_quantity = 0
        total_on_hand_quantity = 0
        total_inventory_cost_value = 0.0
        total_inventory_retail_value = 0.0
        low_stock_product_count = 0
        out_of_stock_product_count = 0

        for prod, disp, on_hand in products:
            disp_qty = disp or 0
            oh_qty = on_hand or 0
            total_qty = disp_qty + oh_qty

            total_display_quantity += disp_qty
            total_on_hand_quantity += oh_qty

            cost_price = float(prod.purchase_price or 0.0)
            selling_price = float(prod.selling_price or 0.0)

            total_inventory_cost_value += total_qty * cost_price
            total_inventory_retail_value += total_qty * selling_price

            if total_qty == 0:
                out_of_stock_product_count += 1
            elif total_qty <= low_stock_threshold:
                low_stock_product_count += 1

        total_inventory_quantity = total_display_quantity + total_on_hand_quantity

        return {
            "total_products": total_products,
            "total_display_quantity": total_display_quantity,
            "total_on_hand_quantity": total_on_hand_quantity,
            "total_inventory_quantity": total_inventory_quantity,
            "total_inventory_cost_value": round(total_inventory_cost_value, 2),
            "total_inventory_retail_value": round(total_inventory_retail_value, 2),
            "low_stock_product_count": low_stock_product_count,
            "out_of_stock_product_count": out_of_stock_product_count,
        }

    def get_daily_sales_trend(self, start_date: datetime, end_date: datetime) -> list[dict]:
        """Aggregate daily gross sales, refunds, net revenue, and transaction counts."""
        # 1. Aggregate Sales by date
        sales_by_date = (
            self.db.query(
                cast(Sale.created_at, Date).label("sale_date"),
                func.sum(Sale.total_amount).label("gross_revenue"),
                func.count(Sale.id).label("transaction_count"),
            )
            .filter(
                Sale.status == SaleStatus.COMPLETED,
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
            )
            .group_by("sale_date")
            .all()
        )

        sales_map = {
            str(r.sale_date): {
                "gross_revenue": float(r.gross_revenue or 0.0),
                "transaction_count": int(r.transaction_count or 0),
            }
            for r in sales_by_date
        }

        # 2. Aggregate Refunds by date
        refunds_by_date = (
            self.db.query(
                cast(SaleRefund.created_at, Date).label("refund_date"),
                func.sum(SaleRefund.refund_amount).label("total_refunds"),
            )
            .filter(
                SaleRefund.created_at >= start_date,
                SaleRefund.created_at <= end_date,
            )
            .group_by("refund_date")
            .all()
        )

        refunds_map = {
            str(r.refund_date): float(r.total_refunds or 0.0)
            for r in refunds_by_date
        }

        # 3. Merge dates
        all_dates = sorted(set(list(sales_map.keys()) + list(refunds_map.keys())))

        trend_items = []
        for date_str in all_dates:
            s_data = sales_map.get(date_str, {"gross_revenue": 0.0, "transaction_count": 0})
            gross = s_data["gross_revenue"]
            count = s_data["transaction_count"]
            refund = refunds_map.get(date_str, 0.0)
            net = gross - refund

            trend_items.append({
                "date": date_str,
                "gross_revenue": round(gross, 2),
                "refunds": round(refund, 2),
                "net_revenue": round(net, 2),
                "transaction_count": count,
            })

        return trend_items
