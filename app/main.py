from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.responses import create_response
from app.modules.ai.api.ai_router import router as ai_router
from app.modules.analytics.api.analytics_router import router as analytics_router
from app.modules.audit.api.audit_router import router as audit_router
from app.modules.auth.api.auth_router import router as auth_router
from app.modules.inventory.api.inventory_router import router as inventory_router
from app.modules.notifications.api.notifications_router import router as notifications_router
from app.modules.products.api.products_router import router as products_router
from app.modules.sales.api.closing_router import router as closing_router
from app.modules.sales.api.sales_router import router as sales_router
from app.modules.warehouse.api.warehouse_router import router as warehouse_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(inventory_router, prefix=settings.API_V1_STR)
app.include_router(warehouse_router, prefix=settings.API_V1_STR)
app.include_router(sales_router, prefix=settings.API_V1_STR)
app.include_router(closing_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)



@app.get("/health", tags=["System"])
@app.get(f"{settings.API_V1_STR}/health", tags=["System"])
def healthcheck():
    """System healthcheck endpoint."""
    return create_response(
        data={
            "status": "healthy",
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
        }
    )
