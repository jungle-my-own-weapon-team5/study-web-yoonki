from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from dtos.board_dto import BoardCreateRequest, BoardListResponse, BoardResponse, BoardUpdateRequest
from model import Board, User
from routes.auth import get_current_user

router = APIRouter(prefix="/board", tags=["board"])


# 게시글 등록
@router.post("/", response_model=BoardResponse)
def create_board(
        body: BoardCreateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    board = Board(
        title=body.title,
        content=body.content,
        category_id=body.category_id,
        author_id=current_user.id,
    )

    db.add(board)
    db.commit()
    db.refresh(board)

    return board


# 게시글 전체 조회
@router.get("/", response_model=BoardListResponse)
def read_boards(
        page: int = Query(default=1, ge=1),
        size: int = Query(default=10, ge=1, le=100),
        db: Session = Depends(get_db)):
    query = db.query(Board).order_by(Board.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()

    return {
        "items": items,
        "page": page,
        "size": size,
        "total": total,
    }


# 게시글 단일 조회
@router.get("/{board_id}", response_model=BoardResponse)
def read_board(board_id: int, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    return board


# 게시글 수정
@router.patch("/{board_id}", response_model=BoardResponse)
def update_board(
        board_id: int,
        body: BoardUpdateRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if board.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    update_data = body.model_dump(exclude_unset=True, exclude={"tags"})
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(board, field, value)

    db.commit()
    db.refresh(board)

    return board


# 게시글 삭제
@router.delete("/{board_id}")
def delete_board(
        board_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if board.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(board)
    db.commit()

    return {"message": "Board deleted"}
