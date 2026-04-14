from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import redirect, request, url_for

from src.bll.auth_service import AuthService


def require_auth(auth_service: AuthService) -> Callable[..., Any]:
    """Route decorator that requires a valid JWT token in cookie."""

    def decorator(view_func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view_func)
        def wrapped(*args: Any, **kwargs: Any):
            token = request.cookies.get("auth_token")
            payload = auth_service.verify_token(token)
            if payload is None:
                return redirect(url_for("auth.login"))
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
