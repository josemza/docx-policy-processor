from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DatabaseBackend, get_settings



def build_engine():
    settings = get_settings()
    engine_kwargs = {"echo": settings.database_echo, "future": True}
    if settings.database_backend == DatabaseBackend.sqlite:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(settings.database_url, **engine_kwargs)



def get_session_local():
    engine = build_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False), engine



def get_db():
    session_local, _ = get_session_local()
    session = session_local()
    try:
        yield session
    finally:
        session.close()
