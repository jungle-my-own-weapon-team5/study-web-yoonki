from sqlalchemy import Column, DateTime, Integer, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship
from database import Base

class BaseEntity:
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

class User(BaseEntity, Base):
    __tablename__ = 'users'
    
    nickname = Column(String(250), nullable=False, default='익명')
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version}

    boards = relationship("Board", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    board_likes = relationship("BoardLike", back_populates="user")
    
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

    tag_relation = relationship("TagRelation", back_populates="board")

    likes = relationship("BoardLike", back_populates="board")

    comments = relationship("Comment", back_populates="board")

class BoardLike(Base):
    __tablename__ = 'board_like'

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", back_populates="board_likes")
    board_id = Column(Integer, ForeignKey("board.id"), primary_key=True)
    board = relationship("Board", back_populates="likes")

class Tag(BaseEntity, Base):
    __tablename__ = 'tag'

    title = Column(String(250), nullable=False)

    version = Column(Integer, nullable=False, default=1)
    tag_relation = relationship("TagRelation", back_populates="tag")

    __mapper_args__ = {"version_id_col": version}

class TagRelation(Base):
    __tablename__ = 'tag_relation'

    board_id = Column(Integer, ForeignKey("board.id"), primary_key=True)
    board = relationship("Board", back_populates="tag_relation")
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)
    tag = relationship("Tag", back_populates="tag_relation")

class Category(BaseEntity, Base):
    __tablename__ = 'category'

    title = Column(String(250), nullable=False)
    version = Column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version}

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
