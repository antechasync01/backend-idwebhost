import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.products.infrastructure.models import Category, Product, ProductRegistrationRequest, ProductStatus, RegistrationStatus


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------- Category ----------------
    def get_categories(self) -> Sequence[Category]:
        return self.db.scalars(select(Category).order_by(Category.name)).all()

    def get_category_by_id(self, category_id: uuid.UUID) -> Category | None:
        return self.db.get(Category, category_id)

    def get_category_by_name(self, name: str) -> Category | None:
        return self.db.scalar(select(Category).where(Category.name == name))

    def create_category(self, category: Category) -> Category:
        self.db.add(category)
        self.db.flush()
        return category

    # ---------------- Product ----------------
    def get_product_by_id(self, product_id: uuid.UUID) -> Product | None:
        return self.db.get(Product, product_id)

    def get_product_by_gtin(self, gtin: str) -> Product | None:
        return self.db.scalar(select(Product).where(Product.gtin == gtin))

    def list_products(
        self,
        query: str | None = None,
        category_id: uuid.UUID | None = None,
        status: ProductStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Product], int]:
        stmt = select(Product)
        if query:
            pattern = f"%{query}%"
            stmt = stmt.where((Product.name.ilike(pattern)) | (Product.gtin.ilike(pattern)) | (Product.brand.ilike(pattern)))
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if status:
            stmt = stmt.where(Product.status == status)

        total_stmt = select(Product.id).where(*stmt.whereclause.get_children()) if stmt.whereclause is not None else select(Product.id)
        # Simplify count:
        items = self.db.scalars(stmt.order_by(Product.name).offset(skip).limit(limit)).all()
        # For hackathon/MVP count total:
        all_matching = self.db.scalars(stmt).all()
        total = len(all_matching)
        return items, total

    def create_product(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        return product

    def update_product(self, product: Product) -> Product:
        self.db.flush()
        return product

    # ---------------- Product Registration Request ----------------
    def get_registration_request_by_id(self, request_id: uuid.UUID) -> ProductRegistrationRequest | None:
        return self.db.get(ProductRegistrationRequest, request_id)

    def get_pending_registration_by_gtin(self, gtin: str) -> ProductRegistrationRequest | None:
        return self.db.scalar(
            select(ProductRegistrationRequest).where(
                ProductRegistrationRequest.gtin == gtin,
                ProductRegistrationRequest.status == RegistrationStatus.PENDING,
            )
        )

    def list_registration_requests(
        self,
        status: RegistrationStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[ProductRegistrationRequest], int]:
        stmt = select(ProductRegistrationRequest)
        if status:
            stmt = stmt.where(ProductRegistrationRequest.status == status)
        items = self.db.scalars(stmt.order_by(ProductRegistrationRequest.created_at.desc()).offset(skip).limit(limit)).all()
        all_matching = self.db.scalars(stmt).all()
        return items, len(all_matching)

    def create_registration_request(self, request_obj: ProductRegistrationRequest) -> ProductRegistrationRequest:
        self.db.add(request_obj)
        self.db.flush()
        return request_obj

    def update_registration_request(self, request_obj: ProductRegistrationRequest) -> ProductRegistrationRequest:
        self.db.flush()
        return request_obj
