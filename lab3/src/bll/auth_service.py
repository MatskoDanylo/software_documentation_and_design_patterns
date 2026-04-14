from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


class AuthService:
    """Simple JWT authentication service for lab usage."""

    _SECRET_KEY = "lab3-jwt-secret-key"
    _ALGORITHM = "HS256"
    _TOKEN_LIFETIME = timedelta(hours=1)

    def login(self, username: str, password: str) -> str:
        if username != "admin" or password != "admin":
            raise ValueError("Invalid username or password")

        now = datetime.now(timezone.utc)
        payload = {
            "sub": username,
            "role": "admin",
            "iat": now,
            "exp": now + self._TOKEN_LIFETIME,
        }
        return jwt.encode(payload, self._SECRET_KEY, algorithm=self._ALGORITHM)

    def verify_token(self, token: str | None) -> dict[str, Any] | None:
        if not token:
            return None

        try:
            payload = jwt.decode(token, self._SECRET_KEY, algorithms=[self._ALGORITHM])
        except jwt.InvalidTokenError:
            return None

        return payload
