from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from model import Board, Category, Tag, TagRelation


class BoardRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self) -> list[Category]:
        return self.db.query(Category).order_by(Category.title.asc(), Category.id.asc()).all()

    def get_category_by_id(self, category_id: int) -> Category | None:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def add_board(self, board: Board) -> Board:
        self.db.add(board)
        return board

    def get_board_by_id(self, board_id: int) -> Board | None:
        return self.db.query(Board).filter(Board.id == board_id).first()

    def list_boards(
        self,
        page: int,
        size: int,
        search_type: Literal["title", "content"],
        keyword: str | None,
        tag_title: str | None,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> tuple[list[Board], int]:
        query = self.db.query(Board)

        if keyword:
            search_value = f"%{keyword}%"
            search_column = Board.content if search_type == "content" else Board.title
            query = query.filter(search_column.ilike(search_value))

        if tag_title:
            query = (
                query
                .join(Board.tag_relations)
                .join(TagRelation.tag)
                .filter(Tag.title == tag_title)
            )

        if start_at:
            query = query.filter(Board.created_at >= start_at)

        if end_at:
            query = query.filter(Board.created_at <= end_at)

        query = query.order_by(Board.created_at.desc(), Board.id.desc())
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()

        return items, total

    def get_previous_board(self, board: Board) -> Board | None:
        return (
            self.db.query(Board)
            .filter(
                or_(
                    Board.created_at < board.created_at,
                    and_(Board.created_at == board.created_at, Board.id < board.id),
                )
            )
            .order_by(Board.created_at.desc(), Board.id.desc())
            .first()
        )

    def get_next_board(self, board: Board) -> Board | None:
        return (
            self.db.query(Board)
            .filter(
                or_(
                    Board.created_at > board.created_at,
                    and_(Board.created_at == board.created_at, Board.id > board.id),
                )
            )
            .order_by(Board.created_at.asc(), Board.id.asc())
            .first()
        )

    def get_or_create_tag(self, title: str) -> Tag:
        tag = self.db.query(Tag).filter(Tag.title == title).first()

        if not tag:
            tag = Tag(title=title)
            self.db.add(tag)
            self.db.flush()

        return tag

    def replace_board_tags(self, board: Board, tag_titles: list[str]) -> None:
        board.tag_relations.clear()
        self.db.flush()

        for title in tag_titles:
            tag = self.get_or_create_tag(title)
            board.tag_relations.append(TagRelation(tag=tag))

    def delete_board(self, board: Board) -> None:
        self.db.delete(board)
