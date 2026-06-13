from sqlalchemy.orm import Session

from model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def create(self, nickname: str, email: str, password: str) -> User:
        user = User(nickname=nickname, email=email, password=password)
        self.db.add(user)
        return user
