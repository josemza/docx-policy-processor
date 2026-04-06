from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_session_context, get_product_service
from app.core.responses import success_response
from app.domain.products.schemas import ProductResponse
from app.services.products.product_service import ProductService

router = APIRouter()


@router.get("")
async def list_active_products(
    _: object = Depends(get_current_session_context),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    products = product_service.list_active_products()
    return success_response(
        message="Catalogo de productos activo.",
        data=[ProductResponse.model_validate(product).model_dump() for product in products],
    )
