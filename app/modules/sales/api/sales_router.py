from datetime import date
import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, require_permission
from app.core.responses import success_response
from app.modules.products.infrastructure.models import Product
from app.modules.sales.application.sales_service import SalesService
from app.modules.sales.domain.schemas import (
    SaleCreateRequest,
    SaleItemResponse,
    SaleRefundItemResponse,
    SaleRefundRequest,
    SaleRefundResponse,
    SaleResponse,
)
from app.modules.sales.infrastructure.models import SaleStatus
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/sales", tags=["Sales & POS"])


def _to_sale_response(db: Session, sale: Any) -> SaleResponse:
    items_data = []
    for item in sale.items:
        prod = db.get(Product, item.product_id)
        items_data.append(
            SaleItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=prod.name if prod else None,
                gtin=prod.gtin if prod else None,
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                subtotal=float(item.subtotal),
            )
        )

    return SaleResponse(
        id=sale.id,
        receipt_number=sale.receipt_number,
        business_date=sale.business_date,
        cashier_id=sale.cashier_id,
        total_amount=float(sale.total_amount),
        payment_method=sale.payment_method,
        cash_paid=float(sale.cash_paid),
        cash_change=float(sale.cash_change),
        status=sale.status,
        idempotency_key=sale.idempotency_key,
        items=items_data,
        created_at=sale.created_at,
    )


# ---------------- POS Sales Endpoints ----------------
@router.post(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("sales.create"))],
)
def create_sale(
    payload: SaleCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SalesService(db)
    sale = service.create_sale(payload=payload, cashier_id=current_user.id)
    return success_response(
        data=_to_sale_response(db, sale),
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("sales.read"))],
)
def list_sales(
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    cashier_id: uuid.UUID | None = Query(None),
    status_filter: SaleStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = SalesService(db)
    items, total = service.list_sales(
        start_date=start_date,
        end_date=end_date,
        cashier_id=cashier_id,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    data = [_to_sale_response(db, s) for s in items]
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.get(
    "/receipt/{receipt_number}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("sales.read"))],
)
def get_sale_by_receipt(
    receipt_number: str,
    db: Session = Depends(get_db),
):
    service = SalesService(db)
    sale = service.get_sale_by_receipt(receipt_number)
    return success_response(data=_to_sale_response(db, sale))


@router.get(
    "/{sale_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("sales.read"))],
)
def get_sale_by_id(
    sale_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = SalesService(db)
    sale = service.get_sale_by_id(sale_id)
    return success_response(data=_to_sale_response(db, sale))


@router.post(
    "/{sale_id}/void",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("sales.void"))],
)
def void_sale(
    sale_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SalesService(db)
    sale = service.void_sale(sale_id=sale_id, actor_id=current_user.id)
    return success_response(data=_to_sale_response(db, sale))


@router.post(
    "/{sale_id}/refund",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("sales.refund"))],
)
def refund_sale(
    sale_id: uuid.UUID,
    payload: SaleRefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SalesService(db)
    refund = service.refund_sale(
        sale_id=sale_id,
        payload=payload,
        processed_by_id=current_user.id,
    )
    
    items_data = []
    for item in refund.items:
        sale_item = db.get(Product, item.sale_item_id) if hasattr(item, 'sale_item_id') else None
        items_data.append(
            SaleRefundItemResponse(
                id=item.id,
                sale_item_id=item.sale_item_id,
                product_name=sale_item.name if sale_item else None,
                quantity=item.quantity,
                refund_amount=float(item.refund_amount),
            )
        )

    resp = SaleRefundResponse(
        id=refund.id,
        sale_id=refund.sale_id,
        refund_number=refund.refund_number,
        refund_amount=float(refund.refund_amount),
        reason=refund.reason,
        processed_by_id=refund.processed_by_id,
        items=items_data,
        created_at=refund.created_at,
    )
    return success_response(data=resp)
