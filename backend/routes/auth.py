import os

from dtos.auth_dto import LoginRequest, RegisterRequest
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from database import get_db
from model import User
from utils.jwt_util import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_payload
from utils.security import hash_password, verify_password

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


async def get_current_user(
        access_token: str | None = Cookie(default=None),
        db: Session = Depends(get_db)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = get_payload(access_token)
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user


@router.post("/login")
def login(response: Response, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "nickname": user.nickname,
    })
    set_access_token_cookie(response, access_token)

    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
    }


@router.post("/register")
def register(response: Response, body: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == body.email).first()

    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        nickname=body.nickname,
        email=body.email,
        password=hash_password(body.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "nickname": user.nickname,
    })
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
