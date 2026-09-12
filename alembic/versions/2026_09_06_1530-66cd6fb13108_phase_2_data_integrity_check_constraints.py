"""Phase 2 data integrity check constraints

Revision ID: 66cd6fb13108
Revises: 761924d0aa7e
Create Date: 2026-09-06 15:30:11.677771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66cd6fb13108'
down_revision: Union[str, None] = '761924d0aa7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint('ck_inventory_display_qty_non_negative', 'inventory', 'display_quantity >= 0')
    op.create_check_constraint('ck_inventory_on_hand_qty_non_negative', 'inventory', 'on_hand_quantity >= 0')
    op.create_check_constraint('ck_products_purchase_price_non_negative', 'products', 'purchase_price >= 0')
    op.create_check_constraint('ck_products_selling_price_non_negative', 'products', 'selling_price >= 0')
    op.create_check_constraint('ck_sales_total_amount_non_negative', 'sales', 'total_amount >= 0')
    op.create_check_constraint('ck_sales_cash_paid_non_negative', 'sales', 'cash_paid >= 0')
    op.create_check_constraint('ck_sale_items_qty_positive', 'sale_items', 'quantity > 0')
    op.create_check_constraint('ck_sale_items_unit_price_non_negative', 'sale_items', 'unit_price >= 0')
    op.create_check_constraint('ck_sale_items_subtotal_non_negative', 'sale_items', 'subtotal >= 0')
    op.create_check_constraint('ck_cash_closings_opening_cash_non_negative', 'cash_closings', 'opening_cash >= 0')
    op.create_check_constraint('ck_cash_closings_cash_sales_non_negative', 'cash_closings', 'cash_sales >= 0')
    op.create_check_constraint('ck_cash_closings_refunds_non_negative', 'cash_closings', 'refunds >= 0')
    op.create_check_constraint('ck_cash_closings_actual_cash_non_negative', 'cash_closings', 'actual_cash >= 0')
    op.create_check_constraint('ck_receiving_items_qty_positive', 'receiving_items', 'quantity_received > 0')
    op.create_check_constraint('ck_warehouse_requests_qty_positive', 'warehouse_requests', 'requested_quantity > 0')


def downgrade() -> None:
    op.drop_constraint('ck_warehouse_requests_qty_positive', 'warehouse_requests', type_='check')
    op.drop_constraint('ck_receiving_items_qty_positive', 'receiving_items', type_='check')
    op.drop_constraint('ck_cash_closings_actual_cash_non_negative', 'cash_closings', type_='check')
    op.drop_constraint('ck_cash_closings_refunds_non_negative', 'cash_closings', type_='check')
    op.drop_constraint('ck_cash_closings_cash_sales_non_negative', 'cash_closings', type_='check')
    op.drop_constraint('ck_cash_closings_opening_cash_non_negative', 'cash_closings', type_='check')
    op.drop_constraint('ck_sale_items_subtotal_non_negative', 'sale_items', type_='check')
    op.drop_constraint('ck_sale_items_unit_price_non_negative', 'sale_items', type_='check')
    op.drop_constraint('ck_sale_items_qty_positive', 'sale_items', type_='check')
    op.drop_constraint('ck_sales_cash_paid_non_negative', 'sales', type_='check')
    op.drop_constraint('ck_sales_total_amount_non_negative', 'sales', type_='check')
    op.drop_constraint('ck_products_selling_price_non_negative', 'products', type_='check')
    op.drop_constraint('ck_products_purchase_price_non_negative', 'products', type_='check')
    op.drop_constraint('ck_inventory_on_hand_qty_non_negative', 'inventory', type_='check')
    op.drop_constraint('ck_inventory_display_qty_non_negative', 'inventory', type_='check')

