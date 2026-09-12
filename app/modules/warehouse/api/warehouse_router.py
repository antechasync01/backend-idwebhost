import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, require_permission
from app.core.responses import success_response
from app.modules.products.infrastructure.models import Product
from app.modules.suppliers.infrastructure.models import Supplier
from app.modules.users.infrastructure.models import User
from app.modules.warehouse.application.warehouse_service import WarehouseService
from app.modules.warehouse.domain.schemas import (
    ReceivingCreate,
    ReceivingItemResponse,
    ReceivingResponse,
    ReceivingReview,
    WarehouseRequestCreate,
    WarehouseRequestResponse,
    WarehouseRequestReview,
)
from app.modules.warehouse.infrastructure.models import ReceivingStatus, WarehouseRequestStatus

router = APIRouter(prefix="/warehouse", tags=["Warehouse & Receivings"])


# Helper function to convert DB model to Response DTO
def _to_receiving_response(db: Session, rec: Any) -> ReceivingResponse:
    supplier_name = None
    if rec.supplier_id:
        supp = db.get(Supplier, rec.supplier_id)
        supplier_name = supp.name if supp else None

    items_data = []
    for item in rec.items:
        prod = db.get(Product, item.product_id)
        items_data.append(
            ReceivingItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=prod.name if prod else None,
                gtin=prod.gtin if prod else None,
                quantity_received=item.quantity_received,
                unit_cost=item.unit_cost,
            )
        )

    return ReceivingResponse(
        id=rec.id,
        receiving_number=rec.receiving_number,
        supplier_id=rec.supplier_id,
        supplier_name=supplier_name,
        status=rec.status,
        submitted_by_id=rec.submitted_by_id,
        reviewed_by_id=rec.reviewed_by_id,
        notes=rec.notes,
        items=items_data,
        created_at=rec.created_at,
        updated_at=rec.updated_at,
    )


# ---------------- Receiving Endpoints ----------------
@router.get(
    "/receivings",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("receiving.read"))],
)
def list_receivings(
    status_filter: ReceivingStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = WarehouseService(db)
    items, total = service.list_receivings(status=status_filter, skip=skip, limit=limit)
    data = [_to_receiving_response(db, r) for r in items]
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.post(
    "/receivings",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("receiving.submit"))],
)
def submit_receiving(
    payload: ReceivingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    rec = service.submit_receiving(payload=payload, submitted_by=current_user)
    return success_response(
        data=_to_receiving_response(db, rec),
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/receivings/{receiving_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("receiving.read"))],
)
def get_receiving_by_id(
    receiving_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = WarehouseService(db)
    rec = service.get_receiving_by_id(receiving_id)
    return success_response(data=_to_receiving_response(db, rec))


@router.post(
    "/receivings/{receiving_id}/approve",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("receiving.approve"))],
)
def approve_receiving(
    receiving_id: uuid.UUID,
    payload: ReceivingReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    rec = service.approve_receiving(
        receiving_id=receiving_id,
        payload=payload,
        reviewer=current_user,
    )
    return success_response(data=_to_receiving_response(db, rec))


@router.post(
    "/receivings/{receiving_id}/reject",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("receiving.reject"))],
)
def reject_receiving(
    receiving_id: uuid.UUID,
    payload: ReceivingReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    rec = service.reject_receiving(
        receiving_id=receiving_id,
        payload=payload,
        reviewer=current_user,
    )
    return success_response(data=_to_receiving_response(db, rec))


@router.post(
    "/receivings/{receiving_id}/request-correction",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("receiving.request_correction"))],
)
def request_correction(
    receiving_id: uuid.UUID,
    payload: ReceivingReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    rec = service.request_correction(
        receiving_id=receiving_id,
        payload=payload,
        reviewer=current_user,
    )
    return success_response(data=_to_receiving_response(db, rec))


# ---------------- Warehouse Requests Endpoints ----------------
@router.get(
    "/requests",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("inventory.read"))],
)
def list_warehouse_requests(
    status_filter: WarehouseRequestStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = WarehouseService(db)
    items, total = service.list_warehouse_requests(status=status_filter, skip=skip, limit=limit)
    data = []
    for r in items:
        prod = db.get(Product, r.product_id)
        data.append(
            WarehouseRequestResponse(
                id=r.id,
                product_id=r.product_id,
                product_name=prod.name if prod else None,
                requested_quantity=r.requested_quantity,
                notes=r.notes,
                status=r.status,
                requested_by_id=r.requested_by_id,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.post(
    "/requests",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("inventory.read"))],
)
def submit_warehouse_request(
    payload: WarehouseRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    req = service.submit_warehouse_request(payload=payload, requested_by_id=current_user.id)
    prod = db.get(Product, req.product_id)
    resp = WarehouseRequestResponse(
        id=req.id,
        product_id=req.product_id,
        product_name=prod.name if prod else None,
        requested_quantity=req.requested_quantity,
        notes=req.notes,
        status=req.status,
        requested_by_id=req.requested_by_id,
        created_at=req.created_at,
        updated_at=req.updated_at,
    )
    return success_response(data=resp, status_code=status.HTTP_201_CREATED)


@router.post(
    "/requests/{request_id}/resolve",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("inventory.transfer"))],
)
def resolve_warehouse_request(
    request_id: uuid.UUID,
    payload: WarehouseRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = WarehouseService(db)
    req = service.resolve_warehouse_request(
        request_id=request_id,
        payload=payload,
        reviewer=current_user,
    )
    prod = db.get(Product, req.product_id)
    resp = WarehouseRequestResponse(
        id=req.id,
        product_id=req.product_id,
        product_name=prod.name if prod else None,
        requested_quantity=req.requested_quantity,
        notes=req.notes,
        status=req.status,
        requested_by_id=req.requested_by_id,
        created_at=req.created_at,
        updated_at=req.updated_at,
    )
    return success_response(data=resp)
