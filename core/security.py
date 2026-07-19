from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import hashlib

import jwt

from app.core.config import settings

try:
    from passlib.context import CryptContext
except ImportError:  # pragma: no cover - fallback for environments without passlib
    CryptContext = None

if CryptContext is not None:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None


def hash_password(password: str) -> str:
    if pwd_context is not None:
        return pwd_context.hash(password)
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if pwd_context is not None:
        return pwd_context.verify(plain_password, hashed_password)
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password


def create_access_token(subject: str) -> str:
    payload = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
