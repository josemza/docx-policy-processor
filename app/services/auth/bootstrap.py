from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.infrastructure.db.session import get_session_local
from app.repositories.auth.user_repository import SqlAlchemyUserRepository



def bootstrap_admin_user() -> None:
    settings = get_settings()
    if not settings.auth_bootstrap_admin:
        return

    session_local, _ = get_session_local()
    db: Session = session_local()
    try:
        repository = SqlAlchemyUserRepository(db)
        existing = repository.get_by_username(settings.auth_bootstrap_admin_username)
        if existing is not None:
            return

        repository.create_user(
            username=settings.auth_bootstrap_admin_username,
            password_hash=hash_password(settings.auth_bootstrap_admin_password),
            full_name="Administrador Bootstrap",
            role="admin",
            is_active=True,
        )
    finally:
        db.close()
