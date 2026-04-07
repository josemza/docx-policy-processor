from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.format_rules import router as format_rules_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.products import router as products_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(products_router, prefix="/products", tags=["products"])
router.include_router(format_rules_router, prefix="/format-rules", tags=["format-rules"])
router.include_router(documents_router, prefix="/documents", tags=["documents"])
