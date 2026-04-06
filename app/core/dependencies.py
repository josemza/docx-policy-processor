from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError
from app.infrastructure.db.session import get_db
from app.repositories.auth.session_repository import SqlAlchemySessionRepository
from app.repositories.auth.user_repository import SqlAlchemyUserRepository
from app.services.auth.authentication_service import AuthenticationService



def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    return AuthenticationService(
        user_repository=SqlAlchemyUserRepository(db),
        session_repository=SqlAlchemySessionRepository(db),
    )



def get_bearer_token(authorization: str | None = Header(default=None, alias="Authorization")) -> str:
    if authorization is None or not authorization.startswith("Bearer "):
        raise AuthenticationError(
            "Falta el header Authorization Bearer.",
            code="missing_authorization_header",
            status_code=401,
        )
    return authorization.removeprefix("Bearer ").strip()



def get_current_session_context(
    access_token: str = Depends(get_bearer_token),
    auth_service: AuthenticationService = Depends(get_auth_service),
):
    context = auth_service.get_authenticated_session(access_token)
    if not context.user.is_active:
        raise AuthenticationError("El usuario se encuentra inactivo.")
    return context
