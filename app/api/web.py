from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.infrastructure.templating import templates

web_router = APIRouter()


def build_shell_context(
    *,
    page_title: str,
    active_nav: str,
    page_subtitle: str,
    breadcrumbs: list[str],
) -> dict[str, str | list[str]]:
    return {
        "page_title": page_title,
        "page_subtitle": page_subtitle,
        "layout": "shell",
        "view_name": active_nav,
        "active_nav": active_nav,
        "breadcrumbs": breadcrumbs,
        "session_api_base": "/api/v1/auth",
        "deployment_label": "Despliegue local",
        "environment_label": "Local",
        "security_label": "Autenticación activa",
        "session_hint": "Sesión corporativa protegida",
    }


@web_router.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


@web_router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "page_title": "Iniciar sesión",
            "layout": "auth",
            "view_name": "login",
        },
    )


@web_router.get("/app", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=build_shell_context(
            page_title="Nuevo documento",
            active_nav="dashboard",
            page_subtitle="Carga la prepóliza, registra la operación y ejecuta el formateo documental de forma controlada.",
            breadcrumbs=["Workspace", "Nuevo documento"],
        ),
    )


@web_router.get("/app/format-rules", response_class=HTMLResponse, include_in_schema=False)
async def format_rules_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="format_rules.html",
        context=build_shell_context(
            page_title="Reglas de formato",
            active_nav="format_rules",
            page_subtitle="Administra configuraciones versionadas por producto sin afectar la operación documental.",
            breadcrumbs=["Workspace", "Configuración", "Reglas de formato"],
        ),
    )

