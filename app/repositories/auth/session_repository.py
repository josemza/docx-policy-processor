from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.auth.entities import UserSession
from app.infrastructure.db.models.auth import UserSessionModel



def _to_domain(model: UserSessionModel) -> UserSession:
    return UserSession(
        id=model.id,
        user_id=model.user_id,
        refresh_token_hash=model.refresh_token_hash,
        user_agent=model.user_agent,
        client_ip=model.client_ip,
        is_active=model.is_active,
        expires_at=model.expires_at,
        revoked_at=model.revoked_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemySessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(
        self,
        *,
        user_id: str,
        refresh_token_hash: str,
        expires_at: datetime,
        user_agent: str | None = None,
        client_ip: str | None = None,
    ) -> UserSession:
        model = UserSessionModel(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            client_ip=client_ip,
            is_active=True,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _to_domain(model)

    def get_by_id(self, session_id: str) -> UserSession | None:
        model = self.db.get(UserSessionModel, session_id)
        return _to_domain(model) if model else None

    def rotate_refresh_token(
        self,
        *,
        session_id: str,
        refresh_token_hash: str,
        expires_at: datetime,
    ) -> UserSession:
        model = self.db.get(UserSessionModel, session_id)
        if model is None:
            raise ValueError("Session not found")
        model.refresh_token_hash = refresh_token_hash
        model.expires_at = expires_at
        model.revoked_at = None
        model.is_active = True
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _to_domain(model)

    def revoke_session(self, session_id: str) -> None:
        model = self.db.get(UserSessionModel, session_id)
        if model is None:
            return
        model.is_active = False
        model.revoked_at = datetime.now(timezone.utc)
        self.db.add(model)
        self.db.commit()

    def revoke_user_sessions(self, user_id: str) -> None:
        stmt = select(UserSessionModel).where(
            UserSessionModel.user_id == user_id,
            UserSessionModel.is_active.is_(True),
        )
        now = datetime.now(timezone.utc)
        for model in self.db.scalars(stmt):
            model.is_active = False
            model.revoked_at = now
            self.db.add(model)
        self.db.commit()
