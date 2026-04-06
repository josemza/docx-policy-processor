from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import (
    TokenType,
    build_token_payload,
    decode_jwt,
    encode_jwt,
    hash_token,
    verify_password,
    verify_token_hash,
)
from app.domain.auth.entities import SessionContext, User, UserSession
from app.domain.auth.schemas import TokenPair
from app.repositories.auth.session_repository import SqlAlchemySessionRepository
from app.repositories.auth.user_repository import SqlAlchemyUserRepository


class AuthenticationService:
    def __init__(
        self,
        *,
        user_repository: SqlAlchemyUserRepository,
        session_repository: SqlAlchemySessionRepository,
    ) -> None:
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.settings = get_settings()

    def login(
        self,
        *,
        username: str,
        password: str,
        user_agent: str | None = None,
        client_ip: str | None = None,
    ) -> tuple[User, TokenPair]:
        user = self.user_repository.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("Credenciales invalidas.")
        if not user.is_active:
            raise AuthenticationError("El usuario se encuentra inactivo.")

        refresh_expires_at = self._refresh_expiration_datetime()
        session = self.session_repository.create_session(
            user_id=user.id,
            refresh_token_hash="pending",
            expires_at=refresh_expires_at,
            user_agent=user_agent,
            client_ip=client_ip,
        )
        tokens = self._issue_tokens(user=user, session=session)
        self.session_repository.rotate_refresh_token(
            session_id=session.id,
            refresh_token_hash=hash_token(tokens.refresh_token),
            expires_at=refresh_expires_at,
        )
        self.user_repository.update_last_login(user.id, datetime.now(timezone.utc))
        return self.user_repository.get_by_id(user.id) or user, tokens

    def refresh(self, refresh_token: str) -> tuple[User, TokenPair]:
        payload = decode_jwt(refresh_token, expected_type=TokenType.REFRESH)
        session = self._get_active_session(payload["sid"])
        now = datetime.now(timezone.utc)
        if session.expires_at < now:
            self.session_repository.revoke_session(session.id)
            raise AuthenticationError(
                "La sesion de refresh ha expirado.",
                code="session_expired",
                status_code=401,
            )
        if not verify_token_hash(refresh_token, session.refresh_token_hash):
            self.session_repository.revoke_session(session.id)
            raise AuthenticationError(
                "El refresh token no coincide con la sesion activa.",
                code="refresh_token_reused",
                status_code=401,
            )

        user = self.user_repository.get_by_id(session.user_id)
        if user is None or not user.is_active:
            self.session_repository.revoke_session(session.id)
            raise AuthenticationError("La sesion no tiene un usuario valido.")

        tokens = self._issue_tokens(user=user, session=session)
        self.session_repository.rotate_refresh_token(
            session_id=session.id,
            refresh_token_hash=hash_token(tokens.refresh_token),
            expires_at=self._refresh_expiration_datetime(),
        )
        return user, tokens

    def logout(self, refresh_token: str) -> None:
        payload = decode_jwt(refresh_token, expected_type=TokenType.REFRESH)
        session = self._get_active_session(payload["sid"])
        if not verify_token_hash(refresh_token, session.refresh_token_hash):
            self.session_repository.revoke_session(session.id)
            raise AuthenticationError(
                "No fue posible cerrar la sesion actual.",
                code="logout_failed",
                status_code=401,
            )
        self.session_repository.revoke_session(session.id)

    def get_authenticated_session(self, access_token: str) -> SessionContext:
        payload = decode_jwt(access_token, expected_type=TokenType.ACCESS)
        session = self._get_active_session(payload["sid"])
        user = self.user_repository.get_by_id(payload["sub"])
        if user is None or not user.is_active:
            raise AuthenticationError("No existe un usuario activo para este token.")
        return SessionContext(user=user, session=session)

    def _issue_tokens(self, *, user: User, session: UserSession) -> TokenPair:
        access_payload = build_token_payload(
            subject=user.id,
            session_id=session.id,
            token_type=TokenType.ACCESS,
            expires_delta=timedelta(minutes=self.settings.jwt_access_token_minutes),
        )
        refresh_payload = build_token_payload(
            subject=user.id,
            session_id=session.id,
            token_type=TokenType.REFRESH,
            expires_delta=timedelta(minutes=self.settings.jwt_refresh_token_minutes),
        )
        return TokenPair(
            access_token=encode_jwt(access_payload),
            refresh_token=encode_jwt(refresh_payload),
            expires_in=self.settings.jwt_access_token_minutes * 60,
        )

    def _get_active_session(self, session_id: str) -> UserSession:
        session = self.session_repository.get_by_id(session_id)
        if session is None or not session.is_active:
            raise AuthenticationError(
                "La sesion ya no esta activa.",
                code="inactive_session",
                status_code=401,
            )
        return session

    def _refresh_expiration_datetime(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.jwt_refresh_token_minutes
        )
