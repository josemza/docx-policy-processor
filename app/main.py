from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.api.web import web_router
from app.core.config import get_settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import auth  # noqa: F401
from app.infrastructure.db.session import get_session_local
from app.services.auth.bootstrap import bootstrap_admin_user


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    _, engine = get_session_local()
    Base.metadata.create_all(bind=engine)
    bootstrap_admin_user()
    yield



def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    register_exception_handlers(application)
    application.include_router(web_router)
    application.include_router(api_router)
    application.mount("/static", StaticFiles(directory="app/static"), name="static")
    return application


app = create_app()
