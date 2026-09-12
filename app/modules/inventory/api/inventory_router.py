import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, require_permission
from app.core.responses import success_response
from app.modules.inventory.application.inventory_service import InventoryService
from app.modules.inventory.domain.schemas import (
    InventoryAdjustmentRequest,
    InventoryMovementResponse,
    InventoryResponse,
    InventoryTransferRequest,
)
from app.modules.inventory.infrastructure.models import MovementType
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("inventory.read"))],
)
def list_inventory(
    query: str | None = Query(None, description="Search by product name or GTIN"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    items, total = service.list_inventory(query=query, skip=skip, limit=limit)
    
    data = []
    for inv, prod in items:
        resp = InventoryResponse(
            id=inv.id,
            product_id=inv.product_id,
            product_name=prod.name if prod else None,
            gtin=prod.gtin if prod else None,
            display_quantity=inv.display_quantity,
            on_hand_quantity=inv.on_hand_quantity,
            total_available=inv.total_available,
            updated_at=inv.updated_at,
        )
        data.append(resp)
        
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.get(
    "/movements",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("inventory.read"))],
)
def list_movements(
    product_id: uuid.UUID | None = Query(None),
    movement_type: MovementType | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    movements, total = service.list_movements(
        product_id=product_id,
        movement_type=movement_type,
        skip=skip,
        limit=limit,
    )
    
    data = []
    for m, prod in movements:
        resp = InventoryMovementResponse(
            id=m.id,
            product_id=m.product_id,
            product_name=prod.name if prod else None,
            movement_type=m.movement_type,
            quantity=m.quantity,
            from_location=m.from_location,
            to_location=m.to_location,
            reference_type=m.reference_type,
            reference_id=m.reference_id,
            actor_id=m.actor_id,
            occurred_at=m.occurred_at,
            metadata_info=m.metadata_info,
        )
        data.append(resp)
        
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.get(
    "/{product_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("inventory.read"))],
)
def get_inventory_by_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = InventoryService(db)
    inv, prod = service.get_inventory_by_product_id(product_id)
    resp = InventoryResponse(
        id=inv.id,
        product_id=inv.product_id,
        product_name=prod.name if prod else None,
        gtin=prod.gtin if prod else None,
        display_quantity=inv.display_quantity,
        on_hand_quantity=inv.on_hand_quantity,
        total_available=inv.total_available,
        updated_at=inv.updated_at,
    )
    return success_response(data=resp)


@router.post(
    "/transfer",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("inventory.transfer"))],
)
def transfer_stock(
    payload: InventoryTransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InventoryService(db)
    inv, prod = service.transfer_stock(payload=payload, actor_id=current_user.id)
    resp = InventoryResponse(
        id=inv.id,
        product_id=inv.product_id,
        product_name=prod.name if prod else None,
        gtin=prod.gtin if prod else None,
        display_quantity=inv.display_quantity,
        on_hand_quantity=inv.on_hand_quantity,
        total_available=inv.total_available,
        updated_at=inv.updated_at,
    )
    return success_response(data=resp)


@router.post(
    "/adjust",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("inventory.adjust"))],
)
def adjust_inventory(
    payload: InventoryAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InventoryService(db)
    inv, prod = service.adjust_inventory(payload=payload, actor_id=current_user.id)
    resp = InventoryResponse(
        id=inv.id,
        product_id=inv.product_id,
        product_name=prod.name if prod else None,
        gtin=prod.gtin if prod else None,
        display_quantity=inv.display_quantity,
        on_hand_quantity=inv.on_hand_quantity,
        total_available=inv.total_available,
        updated_at=inv.updated_at,
    )
    return success_response(data=resp)
