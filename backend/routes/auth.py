import os

from dependencies.auth import get_current_user
from dependencies.exceptions import to_http_exception
from dependencies.services import get_auth_service
from domain.exceptions import DomainError
from dtos.auth_dto import LoginRequest, RegisterRequest
from fastapi import APIRouter, Depends, Response
from model import User
from services.auth_service import AuthService
from utils.jwt_util import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])

# true: HTTPS요청만 cookie 전송, false: HTTP에도 cookie 전송
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


def set_access_token_cookie(response: Response, access_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )


@router.post("/login")
def login(
        response: Response,
        body: LoginRequest,
        auth_service: AuthService = Depends(get_auth_service)):
    try:
        user = auth_service.login(body)
        access_token = auth_service.create_user_access_token(user)
    except DomainError as exc:
        raise to_http_exception(exc) from exc

    set_access_token_cookie(response, access_token)

    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
    }


@router.post("/register")
def register(
        response: Response,
        body: RegisterRequest,
        auth_service: AuthService = Depends(get_auth_service)):
    try:
        user = auth_service.register(body)
        access_token = auth_service.create_user_access_token(user)
    except DomainError as exc:
        raise to_http_exception(exc) from exc

    set_access_token_cookie(response, access_token)

    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return {"message": "Logged out"}


@router.get("/user")
def response_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nickname": current_user.nickname,
    }
