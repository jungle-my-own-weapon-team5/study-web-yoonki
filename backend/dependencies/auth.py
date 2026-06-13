from fastapi import Cookie, Depends

from dependencies.exceptions import to_http_exception
from dependencies.services import get_auth_service
from domain.exceptions import DomainError
from model import User
from services.auth_service import AuthService


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    try:
        return auth_service.get_current_user(access_token)
    except DomainError as exc:
        raise to_http_exception(exc) from exc
