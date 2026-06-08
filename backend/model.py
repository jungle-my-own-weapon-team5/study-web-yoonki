from sqlalchemy import Column, DateTime, Integer, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship
from database import Base

class BaseEntity:
    id = Column(Integer, primary_key=True, autoincrement=True)
    createdAt = Column(DateTime, nullable=False, server_default=func.now())
    updatedAt = Column(DateTime, nullable=True, onupdate=func.now())

class User(BaseEntity, Base):
    __tablename__ = 'users'
    
    nickname = Column(String(250), nullable=False, default='익명')
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version}

    boards = relationship("Board", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    
class Board(BaseEntity, Base):
    __tablename__ = 'board'

    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)

    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version}

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="boards")

    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="boards")

    comments = relationship("Comment", back_populates="board")

class BoardLike(Base):
    __tablename__ = 'board_like'

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    board_id = Column(Integer, ForeignKey("board.id"), primary_key=True)

class Tag(BaseEntity, Base):
    __tablename__ = 'tag'

    title = Column(String(250), nullable=False)

    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version}

class TagRelation(Base):
    __tablename__ = 'tag_relation'

    board_id = Column(Integer, ForeignKey("board.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)

class Category(BaseEntity, Base):
    __tablename__ = 'category'

    title = Column(String(250), nullable=False)

    boards = relationship("Board", back_populates="category")

class Comment(BaseEntity, Base):
    __tablename__ = 'comment'

    content = Column(String(500), nullable=False)
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version}

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="comments")
    
    board_id = Column(Integer, ForeignKey("board.id"), nullable=False)
    board = relationship("Board", back_populates="comments")
