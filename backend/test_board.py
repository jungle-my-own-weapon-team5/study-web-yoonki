import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from model import Board, Category, User
from routes.auth import get_current_user
from routes.board import router as board_router


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
app.include_router(board_router)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return User(id=1, email="test@example.com", nickname="tester", password="hashed")


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)


class BoardRouteTest(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        db.add(Category(id=1, title="General"))
        db.add(User(id=1, email="test@example.com", nickname="tester", password="hashed"))
        db.commit()
        db.close()

    def test_create_board(self):
        response = client.post(
            "/board/",
            json={
                "title": "First board",
                "content": "Hello",
                "category_id": 1,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "First board")
        self.assertEqual(data["content"], "Hello")
        self.assertEqual(data["author_id"], 1)
        self.assertEqual(data["category_id"], 1)

    def test_read_boards_with_pagination(self):
        db = TestingSessionLocal()
        for index in range(15):
            db.add(
                Board(
                    title=f"Board {index}",
                    content="content",
                    category_id=1,
                    author_id=1,
                )
            )
        db.commit()
        db.close()

        response = client.get("/board/?page=2&size=10")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["page"], 2)
        self.assertEqual(data["size"], 10)
        self.assertEqual(data["total"], 15)
        self.assertEqual(len(data["items"]), 5)

    def test_read_board_not_found(self):
        response = client.get("/board/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Board not found")

    def test_update_board(self):
        board_id = self._create_board()

        response = client.patch(
            f"/board/{board_id}",
            json={"title": "Updated title"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated title")

    def test_update_board_forbidden(self):
        board_id = self._create_board(author_id=2)

        response = client.patch(
            f"/board/{board_id}",
            json={"title": "Blocked update"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Forbidden")

    def test_delete_board(self):
        board_id = self._create_board()

        response = client.delete(f"/board/{board_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Board deleted")

        db = TestingSessionLocal()
        board = db.query(Board).filter(Board.id == board_id).first()
        db.close()
        self.assertIsNone(board)

    def _create_board(self, author_id: int = 1) -> int:
        db = TestingSessionLocal()
        board = Board(
            title="Existing board",
            content="content",
            category_id=1,
            author_id=author_id,
        )
        db.add(board)
        db.commit()
        db.refresh(board)
        board_id = board.id
        db.close()
        return board_id


if __name__ == "__main__":
    unittest.main()
