from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal

from sqlalchemy.orm import Session

from domain.exceptions import BadRequestError, ForbiddenError, NotFoundError
from dtos.board_dto import BoardCreateRequest, BoardUpdateRequest
from model import Board, Category, User
from repositories.board_repository import BoardRepository


class BoardService:
    def __init__(self, db: Session):
        self.db = db
        self.boards = BoardRepository(db)

    def list_categories(self) -> list[Category]:
        return self.boards.list_categories()

    def create_board(self, body: BoardCreateRequest, current_user: User) -> Board:
        self._ensure_category_exists(body.category_id)

        board = Board(
            title=body.title,
            content=body.content,
            category_id=body.category_id,
            author_id=current_user.id,
        )

        self.boards.add_board(board)
        self.boards.replace_board_tags(board, self.normalize_tags(body.tags))
        self._commit()
        self.db.refresh(board)

        return board

    def list_boards(
        self,
        page: int,
        size: int,
        search_type: Literal["title", "content"],
        keyword: str | None,
        tag: str | None,
        start_date: date | None,
        end_date: date | None,
    ) -> dict[str, object]:
        keyword_value = keyword.strip() if keyword else None
        tag_titles = self.normalize_tags([tag] if tag else None)
        tag_title = tag_titles[0] if tag_titles else None
        start_at = datetime.combine(start_date, time.min) if start_date else None
        end_at = datetime.combine(end_date, time.max) if end_date else None

        items, total = self.boards.list_boards(
            page=page,
            size=size,
            search_type=search_type,
            keyword=keyword_value,
            tag_title=tag_title,
            start_at=start_at,
            end_at=end_at,
        )

        return {
            "items": items,
            "page": page,
            "size": size,
            "total": total,
        }

    def get_board(self, board_id: int) -> Board:
        return self._get_board_or_raise(board_id)

    def get_board_neighbors(self, board_id: int) -> dict[str, Board | None]:
        board = self._get_board_or_raise(board_id)

        return {
            "previous": self.boards.get_previous_board(board),
            "next": self.boards.get_next_board(board),
        }

    def update_board(
        self,
        board_id: int,
        body: BoardUpdateRequest,
        current_user: User,
    ) -> Board:
        board = self._get_board_or_raise(board_id)
        self._ensure_author(board, current_user)

        if body.category_id is not None:
            self._ensure_category_exists(body.category_id)

        tags_was_sent = "tags" in body.model_fields_set
        update_data = body.model_dump(exclude_unset=True, exclude={"tags"})
        if not update_data and not tags_was_sent:
            raise BadRequestError("No fields to update")

        for field, value in update_data.items():
            setattr(board, field, value)

        if tags_was_sent:
            self.boards.replace_board_tags(board, self.normalize_tags(body.tags))

        self._commit()
        self.db.refresh(board)

        return board

    def delete_board(self, board_id: int, current_user: User) -> None:
        board = self._get_board_or_raise(board_id)
        self._ensure_author(board, current_user)
        self.boards.delete_board(board)
        self._commit()

    def normalize_tags(self, tags: list[str] | None) -> list[str]:
        normalized_tags: list[str] = []
        seen_titles: set[str] = set()

        for tag in tags or []:
            for token in tag.split():
                title = token.strip().lstrip("#").strip()

                if not title or title in seen_titles:
                    continue

                normalized_tags.append(title)
                seen_titles.add(title)

        return normalized_tags

    def _get_board_or_raise(self, board_id: int) -> Board:
        board = self.boards.get_board_by_id(board_id)

        if not board:
            raise NotFoundError("Board not found")

        return board

    def _ensure_category_exists(self, category_id: int) -> None:
        if not self.boards.get_category_by_id(category_id):
            raise BadRequestError("Category not found")

    def _ensure_author(self, board: Board, current_user: User) -> None:
        if board.author_id != current_user.id:
            raise ForbiddenError("Forbidden")

    def _commit(self) -> None:
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
