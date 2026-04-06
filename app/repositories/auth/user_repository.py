from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.auth.entities import User
from app.infrastructure.db.models.auth import UserModel



def _to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        password_hash=model.password_hash,
        full_name=model.full_name,
        role=model.role,
        is_active=model.is_active,
        last_login_at=model.last_login_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        model = self.db.scalar(stmt)
        return _to_domain(model) if model else None

    def get_by_id(self, user_id: str) -> User | None:
        model = self.db.get(UserModel, user_id)
        return _to_domain(model) if model else None

    def create_user(
        self,
        *,
        username: str,
        password_hash: str,
        full_name: str | None = None,
        role: str = "admin",
        is_active: bool = True,
    ) -> User:
        model = UserModel(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=is_active,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _to_domain(model)

    def update_last_login(self, user_id: str, timestamp: datetime) -> None:
        model = self.db.get(UserModel, user_id)
        if model is None:
            return
        model.last_login_at = timestamp
        self.db.add(model)
        self.db.commit()
