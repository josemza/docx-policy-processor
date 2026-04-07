from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_current_session_context, get_product_service
from app.core.responses import success_response
from app.domain.products.schemas import (
    FormatRuleCreateRequest,
    FormatRuleResponse,
    FormatRuleUpdateRequest,
)
from app.services.products.product_service import ProductService

router = APIRouter()


@router.get("")
async def list_format_rules(
    product_id: str = Query(...),
    _: object = Depends(get_current_session_context),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    rules = product_service.list_format_rules(product_id)
    return success_response(
        message="Listado de reglas de formato.",
        data=[FormatRuleResponse.model_validate(rule).model_dump() for rule in rules],
    )


@router.get("/{rule_id}")
async def get_format_rule(
    rule_id: str,
    _: object = Depends(get_current_session_context),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    rule = product_service.get_format_rule(rule_id)
    return success_response(
        message="Detalle de regla de formato.",
        data=FormatRuleResponse.model_validate(rule).model_dump(),
    )


@router.post("")
async def create_format_rule(
    payload: FormatRuleCreateRequest,
    _: object = Depends(get_current_session_context),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    rule = product_service.create_format_rule(
        product_id=payload.product_id,
        configuration=payload.configuration,
        active=payload.active,
    )
    return success_response(
        message="Regla de formato creada correctamente.",
        data=FormatRuleResponse.model_validate(rule).model_dump(),
    )


@router.put("/{rule_id}")
async def update_format_rule(
    rule_id: str,
    payload: FormatRuleUpdateRequest,
    _: object = Depends(get_current_session_context),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    rule = product_service.update_format_rule(
        rule_id=rule_id,
        configuration=payload.configuration,
        active=payload.active,
    )
    return success_response(
        message="Regla de formato actualizada correctamente.",
        data=FormatRuleResponse.model_validate(rule).model_dump(),
    )


@router.delete("/{rule_id}")
async def delete_format_rule(
    rule_id: str,
    _: object = Depends(get_current_session_context),
    product_service: ProductService = Depends(get_product_service),
) -> dict:
    rule = product_service.delete_format_rule(rule_id)
    return success_response(
        message="Regla de formato desactivada correctamente.",
        data=FormatRuleResponse.model_validate(rule).model_dump(),
    )
