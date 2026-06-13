from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from services.auth_service import AuthService


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)
