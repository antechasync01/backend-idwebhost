import uuid
from typing import Sequence
from sqlalchemy.orm import Session
from app.modules.inventory.infrastructure.models import Inventory
from app.modules.products.domain.exceptions import (
    CategoryNotFoundError,
    DuplicateGTINError,
    InvalidRegistrationStateError,
    ProductNotFoundError,
    RegistrationRequestNotFoundError,
)
from app.modules.products.domain.schemas import (
    CategoryCreate,
    ProductCreate,
    ProductUpdate,
    RegistrationRequestApprove,
    RegistrationRequestCreate,
    RegistrationRequestReject,
)
from app.modules.products.infrastructure.models import Category, Product, ProductRegistrationRequest, ProductStatus, RegistrationStatus
from app.modules.products.infrastructure.product_repository import ProductRepository


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    # ---------------- Category Operations ----------------
    def list_categories(self) -> Sequence[Category]:
        return self.repo.get_categories()

    def create_category(self, payload: CategoryCreate) -> Category:
        existing = self.repo.get_category_by_name(payload.name)
        if existing:
            return existing
        cat = Category(
            id=uuid.uuid4(),
            name=payload.name,
            description=payload.description,
        )
        self.repo.create_category(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    # ---------------- Product Master Operations ----------------
    def list_products(
        self,
        query: str | None = None,
        category_id: uuid.UUID | None = None,
        status: ProductStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Product], int]:
        return self.repo.list_products(query=query, category_id=category_id, status=status, skip=skip, limit=limit)

    def get_product_by_id(self, product_id: uuid.UUID) -> Product:
        product = self.repo.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundError(str(product_id))
        return product

    def get_product_by_gtin(self, gtin: str) -> Product:
        product = self.repo.get_product_by_gtin(gtin)
        if not product:
            raise ProductNotFoundError(gtin)
        return product

    def create_product(self, payload: ProductCreate) -> Product:
        # 1. Validate GTIN uniqueness
        if self.repo.get_product_by_gtin(payload.gtin):
            raise DuplicateGTINError(payload.gtin)

        # 2. Validate Category existence if provided
        if payload.category_id:
            cat = self.repo.get_category_by_id(payload.category_id)
            if not cat:
                raise CategoryNotFoundError(str(payload.category_id))

        # 3. Create Product
        product = Product(
            id=uuid.uuid4(),
            gtin=payload.gtin,
            name=payload.name,
            brand=payload.brand,
            category_id=payload.category_id,
            unit=payload.unit,
            description=payload.description,
            purchase_price=payload.purchase_price,
            selling_price=payload.selling_price,
            status=payload.status,
            external_metadata=payload.external_metadata,
        )
        self.repo.create_product(product)

        # 4. Auto-initialize Inventory row
        inventory = Inventory(
            id=uuid.uuid4(),
            product_id=product.id,
            display_quantity=0,
            on_hand_quantity=0,
        )
        self.db.add(inventory)

        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(self, product_id: uuid.UUID, payload: ProductUpdate) -> Product:
        product = self.get_product_by_id(product_id)

        if payload.category_id is not None:
            cat = self.repo.get_category_by_id(payload.category_id)
            if not cat:
                raise CategoryNotFoundError(str(payload.category_id))
            product.category_id = payload.category_id

        if payload.name is not None:
            product.name = payload.name
        if payload.brand is not None:
            product.brand = payload.brand
        if payload.unit is not None:
            product.unit = payload.unit
        if payload.description is not None:
            product.description = payload.description
        if payload.purchase_price is not None:
            product.purchase_price = payload.purchase_price
        if payload.selling_price is not None:
            product.selling_price = payload.selling_price
        if payload.status is not None:
            product.status = payload.status
        if payload.external_metadata is not None:
            product.external_metadata = payload.external_metadata

        self.repo.update_product(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    # ---------------- Product Registration Workflow Operations ----------------
    def submit_registration_request(
        self,
        payload: RegistrationRequestCreate,
        requested_by_id: uuid.UUID,
    ) -> ProductRegistrationRequest:
        # Check if GTIN already exists in Product Master
        if self.repo.get_product_by_gtin(payload.gtin):
            raise DuplicateGTINError(payload.gtin)

        # Check category if provided
        if payload.suggested_category_id:
            cat = self.repo.get_category_by_id(payload.suggested_category_id)
            if not cat:
                raise CategoryNotFoundError(str(payload.suggested_category_id))

        # Check existing PENDING request
        existing_pending = self.repo.get_pending_registration_by_gtin(payload.gtin)
        if existing_pending:
            return existing_pending

        req_obj = ProductRegistrationRequest(
            id=uuid.uuid4(),
            gtin=payload.gtin,
            suggested_name=payload.suggested_name,
            suggested_category_id=payload.suggested_category_id,
            suggested_unit=payload.suggested_unit,
            suggested_purchase_price=payload.suggested_purchase_price,
            suggested_selling_price=payload.suggested_selling_price,
            status=RegistrationStatus.PENDING,
            requested_by_id=requested_by_id,
        )
        self.repo.create_registration_request(req_obj)
        self.db.commit()
        self.db.refresh(req_obj)
        return req_obj

    def list_registration_requests(
        self,
        status: RegistrationStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[ProductRegistrationRequest], int]:
        return self.repo.list_registration_requests(status=status, skip=skip, limit=limit)

    def approve_registration_request(
        self,
        request_id: uuid.UUID,
        payload: RegistrationRequestApprove,
        reviewed_by_id: uuid.UUID,
    ) -> Product:
        req_obj = self.repo.get_registration_request_by_id(request_id)
        if not req_obj:
            raise RegistrationRequestNotFoundError(str(request_id))

        if req_obj.status != RegistrationStatus.PENDING:
            raise InvalidRegistrationStateError(req_obj.status.value)

        # Update registration status
        req_obj.status = RegistrationStatus.APPROVED
        req_obj.reviewed_by_id = reviewed_by_id
        req_obj.review_notes = payload.review_notes
        self.repo.update_registration_request(req_obj)

        # Create Product Master from suggested fields
        product = Product(
            id=uuid.uuid4(),
            gtin=req_obj.gtin,
            name=req_obj.suggested_name,
            category_id=req_obj.suggested_category_id,
            unit=req_obj.suggested_unit,
            purchase_price=req_obj.suggested_purchase_price or 0.0,
            selling_price=req_obj.suggested_selling_price or 0.0,
            status=ProductStatus.ACTIVE,
        )
        self.repo.create_product(product)

        # Auto-initialize Inventory row
        inventory = Inventory(
            id=uuid.uuid4(),
            product_id=product.id,
            display_quantity=0,
            on_hand_quantity=0,
        )
        self.db.add(inventory)

        self.db.commit()
        self.db.refresh(product)
        return product

    def reject_registration_request(
        self,
        request_id: uuid.UUID,
        payload: RegistrationRequestReject,
        reviewed_by_id: uuid.UUID,
    ) -> ProductRegistrationRequest:
        req_obj = self.repo.get_registration_request_by_id(request_id)
        if not req_obj:
            raise RegistrationRequestNotFoundError(str(request_id))

        if req_obj.status != RegistrationStatus.PENDING:
            raise InvalidRegistrationStateError(req_obj.status.value)

        req_obj.status = RegistrationStatus.REJECTED
        req_obj.reviewed_by_id = reviewed_by_id
        req_obj.review_notes = payload.review_notes

        self.repo.update_registration_request(req_obj)
        self.db.commit()
        self.db.refresh(req_obj)
        return req_obj
