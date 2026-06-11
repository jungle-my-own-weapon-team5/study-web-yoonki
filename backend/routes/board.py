from fastapi import APIRouter

router = APIRouter(prefix="/board", tags=["board"])


@router.get("/")
def read_users():
    return {"board": []}


@router.get("/{board_id}")
def read_user(board_id: int):
    # TODO: 
    return {"board_id": board_id}
