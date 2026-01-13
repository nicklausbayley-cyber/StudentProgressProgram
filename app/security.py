from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError, VerificationError

from app.config import settings
from app.models import Role

ph = PasswordHasher()
ALGO = "HS256"


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError, VerificationError, TypeError, ValueError):
        # Any invalid/mismatched hash should behave like "wrong password", not crash the API
        return False


def create_access_token(subject: str, role: Role) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": subject, "role": role.value, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGO)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGO])
    except JWTError as e:
        raise ValueError("Invalid token") from e
