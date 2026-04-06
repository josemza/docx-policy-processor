from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.infrastructure.templating import templates

web_router = APIRouter()


@web_router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


@web_router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"page_title": "Iniciar sesión", "layout": "auth"},
    )


@web_router.get("/app", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page_title": "Panel principal",
            "layout": "shell",
            "active_nav": "dashboard",
            "session_api_base": "/api/v1/auth",
        },
    )
