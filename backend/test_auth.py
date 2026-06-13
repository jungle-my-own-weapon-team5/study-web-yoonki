import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from model import User
from routes.auth import router as auth_router
from utils.security import hash_password


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
app.include_router(auth_router)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class AuthRouteTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        client.cookies.clear()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_register_success(self):
        response = client.post(
            "/auth/register",
            json={
                "nickname": "tester",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["nickname"], "tester")
        self.assertIn("access_token", response.cookies)

    def test_register_duplicate_email(self):
        payload = {
            "nickname": "tester",
            "email": "test@example.com",
            "password": "password123",
        }
        client.post("/auth/register", json=payload)

        response = client.post("/auth/register", json=payload)

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["detail"], "Email already exists")

    def test_login_success(self):
        self._create_user()

        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "test@example.com")
        self.assertIn("access_token", response.cookies)

    def test_login_wrong_password(self):
        self._create_user()

        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid email or password")

    def test_current_user_requires_cookie(self):
        response = client.get("/auth/user")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated")

    def test_current_user_rejects_invalid_token(self):
        client.cookies.set("access_token", "invalid-token")

        response = client.get("/auth/user")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Could not validate credentials")

    def test_current_user_success(self):
        client.post(
            "/auth/register",
            json={
                "nickname": "tester",
                "email": "test@example.com",
                "password": "password123",
            },
        )

        response = client.get("/auth/user")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "test@example.com")

    def _create_user(self):
        db = TestingSessionLocal()
        user = User(
            nickname="tester",
            email="test@example.com",
            password=hash_password("password123"),
        )
        db.add(user)
        db.commit()
        db.close()


if __name__ == "__main__":
    unittest.main()
