from datetime import date
from typing import Literal

from dependencies.auth import get_current_user
from dependencies.exceptions import to_http_exception
from dependencies.services import get_board_service
from domain.exceptions import DomainError
from dtos.board_dto import (
    BoardCreateRequest,
    BoardListResponse,
    BoardNeighborsResponse,
    BoardResponse,
    BoardUpdateRequest,
    CategoryResponse,
)
from fastapi import APIRouter, Depends, Query
from model import User
from services.board_service import BoardService

router = APIRouter(prefix="/board", tags=["board"])


# 카테고리 목록 조회
@router.get("/categories", response_model=list[CategoryResponse])
def read_categories(board_service: BoardService = Depends(get_board_service)):
    return board_service.list_categories()


# 게시글 등록
@router.post("/", response_model=BoardResponse)
def create_board(
        body: BoardCreateRequest,
        board_service: BoardService = Depends(get_board_service),
        current_user: User = Depends(get_current_user)):
    try:
        return board_service.create_board(body, current_user)
    except DomainError as exc:
        raise to_http_exception(exc) from exc


# 게시글 전체 조회
@router.get("/", response_model=BoardListResponse)
def read_boards(
        page: int = Query(default=1, ge=1),
        size: int = Query(default=10, ge=1, le=100),
        search_type: Literal["title", "content"] = Query(default="title"),
        keyword: str | None = Query(default=None),
        tag: str | None = Query(default=None),
        start_date: date | None = Query(default=None),
        end_date: date | None = Query(default=None),
        board_service: BoardService = Depends(get_board_service)):
    return board_service.list_boards(
        page=page,
        size=size,
        search_type=search_type,
        keyword=keyword,
        tag=tag,
        start_date=start_date,
        end_date=end_date,
    )


# 게시글 이전/다음 조회
@router.get("/{board_id}/neighbors", response_model=BoardNeighborsResponse)
def read_board_neighbors(
        board_id: int,
        board_service: BoardService = Depends(get_board_service)):
    try:
        return board_service.get_board_neighbors(board_id)
    except DomainError as exc:
        raise to_http_exception(exc) from exc


# 게시글 단일 조회
@router.get("/{board_id}", response_model=BoardResponse)
def read_board(
        board_id: int,
        board_service: BoardService = Depends(get_board_service)):
    try:
        return board_service.get_board(board_id)
    except DomainError as exc:
        raise to_http_exception(exc) from exc


# 게시글 수정
@router.patch("/{board_id}", response_model=BoardResponse)
def update_board(
        board_id: int,
        body: BoardUpdateRequest,
        board_service: BoardService = Depends(get_board_service),
        current_user: User = Depends(get_current_user)):
    try:
        return board_service.update_board(board_id, body, current_user)
    except DomainError as exc:
        raise to_http_exception(exc) from exc


# 게시글 삭제
@router.delete("/{board_id}")
def delete_board(
        board_id: int,
        board_service: BoardService = Depends(get_board_service),
        current_user: User = Depends(get_current_user)):
    try:
        board_service.delete_board(board_id, current_user)
    except DomainError as exc:
        raise to_http_exception(exc) from exc

    return {"message": "Board deleted"}
