import uuid
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db, require_permission
from app.core.responses import success_response
from app.modules.products.application.product_service import ProductService
from app.modules.products.domain.schemas import (
    CategoryCreate,
    CategoryResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    RegistrationRequestApprove,
    RegistrationRequestCreate,
    RegistrationRequestReject,
    RegistrationRequestResponse,
)
from app.modules.products.infrastructure.models import ProductStatus, RegistrationStatus
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------- Category Endpoints ----------------
@router.get(
    "/categories",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.read"))],
)
def list_categories(db: Session = Depends(get_db)):
    service = ProductService(db)
    categories = service.list_categories()
    items = [CategoryResponse.model_validate(c) for c in categories]
    return success_response(data=items)


@router.post(
    "/categories",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("product.create"))],
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    cat = service.create_category(payload)
    return success_response(data=CategoryResponse.model_validate(cat), status_code=status.HTTP_201_CREATED)


# ---------------- Registration Requests Endpoints (Must be before /{product_id}) ----------------
@router.get(
    "/registration-requests",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.read"))],
)
def list_registration_requests(
    status_filter: RegistrationStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    items, total = service.list_registration_requests(status=status_filter, skip=skip, limit=limit)
    data = [RegistrationRequestResponse.model_validate(i) for i in items]
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.post(
    "/registration-requests",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("product.create"))],
)
def submit_registration_request(
    payload: RegistrationRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    req_obj = service.submit_registration_request(payload, requested_by_id=current_user.id)
    return success_response(data=RegistrationRequestResponse.model_validate(req_obj), status_code=status.HTTP_201_CREATED)


@router.post(
    "/registration-requests/{request_id}/approve",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.approve"))],
)
def approve_registration_request(
    request_id: uuid.UUID,
    payload: RegistrationRequestApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    product = service.approve_registration_request(
        request_id=request_id,
        payload=payload,
        reviewed_by_id=current_user.id,
    )
    return success_response(data=ProductResponse.model_validate(product))


@router.post(
    "/registration-requests/{request_id}/reject",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.approve"))],
)
def reject_registration_request(
    request_id: uuid.UUID,
    payload: RegistrationRequestReject,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProductService(db)
    req_obj = service.reject_registration_request(
        request_id=request_id,
        payload=payload,
        reviewed_by_id=current_user.id,
    )
    return success_response(data=RegistrationRequestResponse.model_validate(req_obj))


# ---------------- Product Master Endpoints ----------------
@router.get(
    "",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.read"))],
)
def list_products(
    query: str | None = Query(None, description="Search by name, GTIN, or brand"),
    category_id: uuid.UUID | None = Query(None),
    status_filter: ProductStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    items, total = service.list_products(
        query=query,
        category_id=category_id,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    data = [ProductResponse.model_validate(p) for p in items]
    return success_response(data=data, meta={"total": total, "skip": skip, "limit": limit})


@router.get(
    "/gtin/{gtin}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.read"))],
)
def get_product_by_gtin(
    gtin: str,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    product = service.get_product_by_gtin(gtin)
    return success_response(data=ProductResponse.model_validate(product))


@router.get(
    "/{product_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.read"))],
)
def get_product_by_id(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    product = service.get_product_by_id(product_id)
    return success_response(data=ProductResponse.model_validate(product))


@router.post(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("product.create"))],
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    product = service.create_product(payload)
    return success_response(data=ProductResponse.model_validate(product), status_code=status.HTTP_201_CREATED)


@router.put(
    "/{product_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(require_permission("product.update"))],
)
def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    product = service.update_product(product_id, payload)
    return success_response(data=ProductResponse.model_validate(product))
