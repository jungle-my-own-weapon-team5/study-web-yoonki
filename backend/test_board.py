import unittest
from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from model import Board, Category, User
from dependencies.auth import get_current_user
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
    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        db.add(Category(id=1, title="General"))
        db.add(Category(id=2, title="Tech"))
        db.add(User(id=1, email="test@example.com", nickname="tester", password="hashed"))
        db.commit()
        db.close()

    def test_read_categories(self):
        response = client.get("/board/categories")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual([category["title"] for category in data], ["General", "Tech"])

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
        self.assertEqual(data["category"]["title"], "General")
        self.assertEqual(data["tags"], [])

    def test_create_board_with_tags(self):
        response = client.post(
            "/board/",
            json={
                "title": "Tagged board",
                "content": "Hello",
                "category_id": 1,
                "tags": ["#python", "fastapi", "#python", " "],
            },
        )

        self.assertEqual(response.status_code, 200)
        tag_titles = sorted(tag["title"] for tag in response.json()["tags"])
        self.assertEqual(tag_titles, ["fastapi", "python"])

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

    def test_read_boards_with_title_search(self):
        self._create_board(title="React guide", content="frontend")
        self._create_board(title="FastAPI guide", content="React backend")

        response = client.get("/board/?search_type=title&keyword=React")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["title"], "React guide")

    def test_read_boards_with_content_search(self):
        self._create_board(title="React guide", content="frontend")
        self._create_board(title="FastAPI guide", content="React backend")

        response = client.get("/board/?search_type=content&keyword=React")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["title"], "FastAPI guide")

    def test_read_boards_with_tag_filter(self):
        client.post(
            "/board/",
            json={
                "title": "Python board",
                "content": "content",
                "category_id": 1,
                "tags": ["#python"],
            },
        )
        client.post(
            "/board/",
            json={
                "title": "React board",
                "content": "content",
                "category_id": 1,
                "tags": ["#react"],
            },
        )

        response = client.get("/board/?tag=%23python")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["title"], "Python board")

    def test_read_boards_with_date_filter(self):
        self._create_board(title="Old board", created_at=datetime(2026, 1, 1, 10, 0, 0))
        self._create_board(title="Target board", created_at=datetime(2026, 1, 2, 10, 0, 0))
        self._create_board(title="New board", created_at=datetime(2026, 1, 3, 10, 0, 0))

        response = client.get("/board/?start_date=2026-01-02&end_date=2026-01-02")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["title"], "Target board")

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

    def test_update_board_tags(self):
        board_id = self._create_board()

        response = client.patch(
            f"/board/{board_id}",
            json={"tags": ["#updated", "#backend"]},
        )

        self.assertEqual(response.status_code, 200)
        tag_titles = sorted(tag["title"] for tag in response.json()["tags"])
        self.assertEqual(tag_titles, ["backend", "updated"])

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

    def test_read_board_neighbors(self):
        older_id = self._create_board(title="Older", created_at=datetime(2026, 1, 1, 10, 0, 0))
        current_id = self._create_board(title="Current", created_at=datetime(2026, 1, 2, 10, 0, 0))
        newer_id = self._create_board(title="Newer", created_at=datetime(2026, 1, 3, 10, 0, 0))

        response = client.get(f"/board/{current_id}/neighbors")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["previous"]["id"], older_id)
        self.assertEqual(data["next"]["id"], newer_id)

    def _create_board(
        self,
        author_id: int = 1,
        title: str = "Existing board",
        content: str = "content",
        created_at: datetime | None = None,
    ) -> int:
        db = TestingSessionLocal()
        board = Board(
            title=title,
            content=content,
            category_id=1,
            author_id=author_id,
        )

        if created_at:
            board.created_at = created_at

        db.add(board)
        db.commit()
        db.refresh(board)
        board_id = board.id
        db.close()
        return board_id


if __name__ == "__main__":
    unittest.main()
