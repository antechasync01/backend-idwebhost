from datetime import date
import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, require_permission
from app.core.responses import success_response
from app.modules.products.infrastructure.models import Product
from app.modules.sales.application.closing_service import ClosingService
from app.modules.sales.domain.schemas import (
    CashClosingRequest,
    CashClosingResponse,
    CashClosingSummaryResponse,
    DailyClosingResponse,
    InventoryClosingItemResponse,
    InventoryClosingRequest,
    InventoryClosingResponse,
)
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/closing", tags=["Daily Closing"])


def _to_daily_closing_response(db: Session, dc: Any) -> DailyClosingResponse:
    cash_resp = None
    if dc.cash_closing:
        cc = dc.cash_closing
        cash_resp = CashClosingResponse(
            id=cc.id,
            daily_closing_id=cc.daily_closing_id,
            cashier_id=cc.cashier_id,
            opening_cash=float(cc.opening_cash),
            cash_sales=float(cc.cash_sales),
            refunds=float(cc.refunds),
            cash_adjustment=float(cc.cash_adjustment),
            adjustment_notes=cc.adjustment_notes,
            expected_cash=float(cc.expected_cash),
            actual_cash=float(cc.actual_cash),
            variance=float(cc.variance),
            notes=cc.notes,
            created_at=cc.created_at,
        )

    inv_resp = None
    if dc.inventory_closing:
        ic = dc.inventory_closing
        items_data = []
        for item in ic.items:
            prod = db.get(Product, item.product_id)
            items_data.append(
                InventoryClosingItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=prod.name if prod else None,
                    opening_display_quantity=item.opening_display_quantity,
                    opening_on_hand_quantity=item.opening_on_hand_quantity,
                    receiving_quantity=item.receiving_quantity,
                    sales_quantity=item.sales_quantity,
                    adjustment_quantity=item.adjustment_quantity,
                    return_quantity=item.return_quantity,
                    expected_display_quantity=item.expected_display_quantity,
                    expected_on_hand_quantity=item.expected_on_hand_quantity,
                    physical_display_quantity=item.physical_display_quantity,
                    physical_on_hand_quantity=item.physical_on_hand_quantity,
                    display_variance=item.display_variance,
                    on_hand_variance=item.on_hand_variance,
                    status=ic.status.value if hasattr(ic.status, "value") else str(ic.status),
                )
            )
        inv_resp = InventoryClosingResponse(
            id=ic.id,
            daily_closing_id=ic.daily_closing_id,
            status=ic.status.value if hasattr(ic.status, "value") else str(ic.status),
            notes=ic.notes,
            items=items_data,
            created_at=ic.created_at,
        )

    return DailyClosingResponse(
        id=dc.id,
        business_date=dc.business_date,
        status=dc.status.value if hasattr(dc.status, "value") else str(dc.status),
        closed_by_id=dc.closed_by_id,
        cash_closing=cash_resp,
        inventory_closing=inv_resp,
        created_at=dc.created_at,
        updated_at=dc.updated_at,
    )


# ---------------- Daily Closing Endpoints ----------------
@router.get(
    "/today",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("closing.cash"))],
)
def get_today_closing_status(db: Session = Depends(get_db)):
    service = ClosingService(db)
    dc = service.repo.get_or_create_daily_closing(date.today())
    return success_response(data=_to_daily_closing_response(db, dc))


@router.get(
    "/cash/summary",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("closing.cash"))],
)
def get_cash_closing_summary(
    opening_cash: float = Query(0.0, ge=0.0),
    db: Session = Depends(get_db),
):
    service = ClosingService(db)
    summary = service.get_cash_closing_summary(business_date=date.today(), opening_cash=opening_cash)
    return success_response(data=summary)


@router.post(
    "/cash",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("closing.cash"))],
)
def submit_cash_closing(
    payload: CashClosingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ClosingService(db)
    cash_closing = service.submit_cash_closing(payload=payload, cashier_id=current_user.id)
    resp = CashClosingResponse(
        id=cash_closing.id,
        daily_closing_id=cash_closing.daily_closing_id,
        cashier_id=cash_closing.cashier_id,
        opening_cash=float(cash_closing.opening_cash),
        cash_sales=float(cash_closing.cash_sales),
        refunds=float(cash_closing.refunds),
        cash_adjustment=float(cash_closing.cash_adjustment),
        adjustment_notes=cash_closing.adjustment_notes,
        expected_cash=float(cash_closing.expected_cash),
        actual_cash=float(cash_closing.actual_cash),
        variance=float(cash_closing.variance),
        notes=cash_closing.notes,
        created_at=cash_closing.created_at,
    )
    return success_response(data=resp, status_code=status.HTTP_201_CREATED)


@router.post(
    "/inventory",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("closing.inventory"))],
)
def submit_inventory_closing(
    payload: InventoryClosingRequest,
    db: Session = Depends(get_db),
):
    service = ClosingService(db)
    inv_closing = service.submit_inventory_closing(payload=payload)
    items_data = []
    for item in inv_closing.items:
        prod = db.get(Product, item.product_id)
        items_data.append(
            InventoryClosingItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=prod.name if prod else None,
                opening_display_quantity=item.opening_display_quantity,
                opening_on_hand_quantity=item.opening_on_hand_quantity,
                receiving_quantity=item.receiving_quantity,
                sales_quantity=item.sales_quantity,
                adjustment_quantity=item.adjustment_quantity,
                return_quantity=item.return_quantity,
                expected_display_quantity=item.expected_display_quantity,
                expected_on_hand_quantity=item.expected_on_hand_quantity,
                physical_display_quantity=item.physical_display_quantity,
                physical_on_hand_quantity=item.physical_on_hand_quantity,
                display_variance=item.display_variance,
                on_hand_variance=item.on_hand_variance,
                status=item.status.value if hasattr(item.status, "value") else str(item.status),
            )
        )
    resp = InventoryClosingResponse(
        id=inv_closing.id,
        daily_closing_id=inv_closing.daily_closing_id,
        status=inv_closing.status.value if hasattr(inv_closing.status, "value") else str(inv_closing.status),
        notes=inv_closing.notes,
        items=items_data,
        created_at=inv_closing.created_at,
    )
    return success_response(data=resp, status_code=status.HTTP_201_CREATED)


@router.post(
    "/daily/finalize",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("closing.daily"))],
)
def finalize_daily_closing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ClosingService(db)
    dc = service.finalize_daily_closing(closed_by_id=current_user.id)
    return success_response(data=_to_daily_closing_response(db, dc))


@router.get(
    "/history",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("closing.daily"))],
)
def list_daily_closings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ClosingService(db)
    items, total = service.list_daily_closings(skip=skip, limit=limit)
    data = [_to_daily_closing_response(db, dc) for dc in items]
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})
