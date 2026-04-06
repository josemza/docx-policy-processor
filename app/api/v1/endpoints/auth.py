from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_auth_service, get_current_session_context
from app.core.responses import success_response
from app.domain.auth.schemas import LoginRequest, RefreshRequest, SessionUserResponse
from app.services.auth.authentication_service import AuthenticationService

router = APIRouter()


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> dict:
    user, tokens = auth_service.login(
        username=payload.username,
        password=payload.password,
        user_agent=request.headers.get("user-agent"),
        client_ip=request.client.host if request.client else None,
    )
    return success_response(
        message="Inicio de sesion exitoso.",
        data={
            "user": SessionUserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        },
    )


@router.post("/refresh")
async def refresh(
    payload: RefreshRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> dict:
    user, tokens = auth_service.refresh(payload.refresh_token)
    return success_response(
        message="Sesion renovada correctamente.",
        data={
            "user": SessionUserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        },
    )


@router.post("/logout")
async def logout(
    payload: RefreshRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> dict:
    auth_service.logout(payload.refresh_token)
    return success_response(message="Sesion cerrada correctamente.", data=None)


@router.get("/me")
async def me(context=Depends(get_current_session_context)) -> dict:
    return success_response(
        message="Sesion activa.",
        data={"user": SessionUserResponse.model_validate(context.user).model_dump()},
    )
