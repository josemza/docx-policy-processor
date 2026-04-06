from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def test_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Generator[None, None, None]:
    db_path = tmp_path / "test_auth.db"
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DATABASE_BACKEND", "sqlite")
    monkeypatch.setenv("DATABASE_SQLITE_PATH", str(db_path))
    monkeypatch.setenv("AUTH_BOOTSTRAP_ADMIN", "false")

    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    from app.core.security import hash_password
    from app.infrastructure.db.base import Base
    from app.infrastructure.db.models.auth import UserModel
    from app.infrastructure.db.session import get_session_local
    from app.main import create_app

    session_local, engine = get_session_local()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = session_local()
    try:
        db.add(
            UserModel(
                username="admin",
                password_hash=hash_password("admin12345"),
                full_name="Admin Test",
                role="admin",
                is_active=True,
            )
        )
        db.commit()
    finally:
        db.close()

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)
