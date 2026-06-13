from __future__ import annotations

from sqlalchemy.orm import Session

from domain.exceptions import ConflictError, UnauthorizedError
from dtos.auth_dto import LoginRequest, RegisterRequest
from model import User
from repositories.user_repository import UserRepository
from utils.jwt_util import create_access_token, get_payload
from utils.security import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def login(self, body: LoginRequest) -> User:
        user = self.users.get_by_email(body.email)

        if not user or not verify_password(body.password, user.password):
            raise UnauthorizedError("Invalid email or password")

        return user

    def register(self, body: RegisterRequest) -> User:
        if self.users.email_exists(body.email):
            raise ConflictError("Email already exists")

        user = self.users.create(
            nickname=body.nickname,
            email=body.email,
            password=hash_password(body.password),
        )

        self._commit()
        self.db.refresh(user)

        return user

    def get_current_user(self, access_token: str | None) -> User:
        if not access_token:
            raise UnauthorizedError("Not authenticated")

        try:
            payload = get_payload(access_token)
        except ValueError as exc:
            raise UnauthorizedError(str(exc)) from exc

        try:
            user_id = int(payload.get("sub"))
        except (TypeError, ValueError) as exc:
            raise UnauthorizedError("Invalid token") from exc

        user = self.users.get_by_id(user_id)

        if not user:
            raise UnauthorizedError("Invalid token")

        return user

    def create_user_access_token(self, user: User) -> str:
        return create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "nickname": user.nickname,
        })

    def _commit(self) -> None:
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
