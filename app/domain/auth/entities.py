from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    id: str
    username: str
    password_hash: str
    full_name: str | None
    role: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class UserSession:
    id: str
    user_id: str
    refresh_token_hash: str
    user_agent: str | None
    client_ip: str | None
    is_active: bool
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(slots=True)
class SessionContext:
    user: User
    session: UserSession
