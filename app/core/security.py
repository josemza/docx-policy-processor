from datetime import datetime, timedelta, timezone
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError

password_hasher = PasswordHasher()


class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"



def hash_password(password: str) -> str:
    return password_hasher.hash(password)



def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(hashed_password, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False



def hash_token(token: str) -> str:
    return password_hasher.hash(token)



def verify_token_hash(token: str, token_hash: str) -> bool:
    try:
        return password_hasher.verify(token_hash, token)
    except VerifyMismatchError:
        return False
    except Exception:
        return False



def build_token_payload(*, subject: str, session_id: str, token_type: str, expires_delta: timedelta) -> dict:
    settings = get_settings()
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + expires_delta
    return {
        "sub": subject,
        "sid": session_id,
        "type": token_type,
        "jti": str(uuid4()),
        "iss": settings.jwt_issuer,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }



def encode_jwt(payload: dict) -> str:
    settings = get_settings()
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)



def decode_jwt(token: str, expected_type: str | None = None) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError(
            "El token ha expirado.", code="token_expired", status_code=401
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError(
            "El token no es valido.", code="invalid_token", status_code=401
        ) from exc

    if expected_type and payload.get("type") != expected_type:
        raise AuthenticationError(
            "El tipo de token no es valido.",
            code="invalid_token_type",
            status_code=401,
        )
    return payload
