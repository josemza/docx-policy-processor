from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("", summary="Health check")
async def health_check() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment.value,
        "api_version": "v1",
    }
