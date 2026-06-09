from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def read_users():
    return {"users": []}


@router.get("/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id}
