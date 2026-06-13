from __future__ import annotations

import os
import random
from datetime import datetime, timedelta

from database import Base, engine, session
from model import Board, BoardLike, Category, Comment, Tag, TagRelation, User
from utils.security import hash_password


RANDOM_SEED = 20260612
POST_COUNTS = [5, 10, 20, 40, 80]
COMMENTS_PER_USER = 10
LIKES_PER_USER = 10
TEST_PASSWORD = os.getenv("MOCK_USER_PASSWORD", "Test1234!")

CATEGORY_TITLES = ["일상", "개발", "질문", "회고", "정보공유"]
TAG_TITLES = [
    "react",
    "fastapi",
    "postgresql",
    "typescript",
    "python",
    "frontend",
    "backend",
    "study",
    "til",
    "debugging",
]

NICKNAME_ADJECTIVES = [
    "고요한",
    "다정한",
    "맑은",
    "반짝이는",
    "산뜻한",
    "차분한",
    "포근한",
    "푸른",
]
NICKNAME_NOUNS = [
    "가람",
    "구름",
    "달빛",
    "바다",
    "새벽",
    "숲길",
    "은하",
    "하루",
]

POST_TOPICS = [
    "React 상태 관리 정리",
    "FastAPI 라우터 구현 메모",
    "PostgreSQL 쿼리 튜닝 기록",
    "TypeScript 타입 설계 고민",
    "게시판 페이지네이션 테스트",
    "로그인 흐름 점검",
    "컴포넌트 분리 회고",
    "검색 필터 개선 아이디어",
    "태그 기능 사용 후기",
    "오늘의 디버깅 노트",
]

COMMENT_TEMPLATES = [
    "좋은 정리 감사합니다. 테스트하면서 참고해볼게요.",
    "이 부분은 실제 케이스에서도 유용해 보입니다.",
    "비슷한 문제를 봤는데 이 접근이 깔끔하네요.",
    "예시 데이터로 확인하기 좋은 내용입니다.",
    "다음 단계에서 성능도 같이 보면 좋겠습니다.",
    "태그로 다시 찾기 쉬워서 편하네요.",
    "구현 흐름이 잘 보여서 이해하기 쉽습니다.",
    "저도 같은 방식으로 한번 확인해보겠습니다.",
    "에러 케이스까지 추가하면 더 좋아질 것 같습니다.",
    "목록 화면에서 바로 확인해볼 수 있겠네요.",
]


def build_account_specs() -> list[dict[str, object]]:
    rng = random.Random(RANDOM_SEED)
    nicknames: list[str] = []

    while len(nicknames) < len(POST_COUNTS):
        nickname = f"{rng.choice(NICKNAME_ADJECTIVES)}{rng.choice(NICKNAME_NOUNS)}"
        if nickname not in nicknames:
            nicknames.append(nickname)

    return [
        {
            "email": f"test{index:02d}@example.com",
            "nickname": nicknames[index - 1],
            "post_count": post_count,
        }
        for index, post_count in enumerate(POST_COUNTS, start=1)
    ]


ACCOUNT_SPECS = build_account_specs()


def reset_existing_mock_data(db) -> None:
    seed_emails = [str(account["email"]) for account in ACCOUNT_SPECS]
    seed_users = db.query(User).filter(User.email.in_(seed_emails)).all()

    if not seed_users:
        return

    seed_user_ids = [user.id for user in seed_users]
    seed_board_ids = [
        board_id
        for (board_id,) in db.query(Board.id)
        .filter(Board.author_id.in_(seed_user_ids))
        .all()
    ]

    if seed_board_ids:
        db.query(BoardLike).filter(BoardLike.board_id.in_(seed_board_ids)).delete(
            synchronize_session=False
        )
        db.query(Comment).filter(Comment.board_id.in_(seed_board_ids)).delete(
            synchronize_session=False
        )
        db.query(TagRelation).filter(TagRelation.board_id.in_(seed_board_ids)).delete(
            synchronize_session=False
        )

    db.query(BoardLike).filter(BoardLike.user_id.in_(seed_user_ids)).delete(
        synchronize_session=False
    )
    db.query(Comment).filter(Comment.author_id.in_(seed_user_ids)).delete(
        synchronize_session=False
    )
    db.query(Board).filter(Board.author_id.in_(seed_user_ids)).delete(
        synchronize_session=False
    )
    db.query(User).filter(User.id.in_(seed_user_ids)).delete(synchronize_session=False)
    db.flush()


def get_or_create_categories(db) -> list[Category]:
    categories: list[Category] = []

    for title in CATEGORY_TITLES:
        category = db.query(Category).filter(Category.title == title).first()
        if not category:
            category = Category(title=title)
            db.add(category)
            db.flush()
        categories.append(category)

    return categories


def get_or_create_tags(db) -> dict[str, Tag]:
    tags: dict[str, Tag] = {}

    for title in TAG_TITLES:
        tag = db.query(Tag).filter(Tag.title == title).first()
        if not tag:
            tag = Tag(title=title)
            db.add(tag)
            db.flush()
        tags[title] = tag

    return tags


def create_users(db) -> list[User]:
    users: list[User] = []

    for account in ACCOUNT_SPECS:
        user = User(
            email=str(account["email"]),
            nickname=str(account["nickname"]),
            password=hash_password(TEST_PASSWORD),
        )
        db.add(user)
        users.append(user)

    db.flush()
    return users


def build_post_content(nickname: str, post_index: int, topic: str) -> str:
    return (
        f"{nickname}의 {post_index}번째 mock 게시글입니다.\n\n"
        f"주제는 '{topic}'이고, 목록/검색/상세 화면을 확인하기 위한 테스트 데이터입니다. "
        "내용 검색, 날짜 필터, 태그 필터를 확인할 수 있도록 충분한 문장으로 구성했습니다.\n\n"
        "FastAPI와 React 게시판 흐름에서 더미 데이터가 자연스럽게 보이도록 작성했습니다."
    )


def create_boards(
    db,
    users: list[User],
    categories: list[Category],
    tags: dict[str, Tag],
    rng: random.Random,
) -> list[Board]:
    boards: list[Board] = []
    base_created_at = datetime.now() - timedelta(days=30)

    for user, account in zip(users, ACCOUNT_SPECS, strict=True):
        post_count = int(account["post_count"])

        for index in range(1, post_count + 1):
            topic = rng.choice(POST_TOPICS)
            category = rng.choice(categories)
            selected_tags = rng.sample(TAG_TITLES, k=rng.randint(1, 3))
            board = Board(
                title=f"{topic} #{index:03d}",
                content=build_post_content(user.nickname, index, topic),
                author_id=user.id,
                category_id=category.id,
                created_at=base_created_at + timedelta(hours=len(boards) * 3),
            )
            board.tag_relations = [TagRelation(tag=tags[title]) for title in selected_tags]
            db.add(board)
            boards.append(board)

    db.flush()
    return boards


def create_comments(db, users: list[User], boards: list[Board], rng: random.Random) -> int:
    comment_count = 0

    for user in users:
        candidate_boards = [board for board in boards if board.author_id != user.id] or boards
        for board in rng.sample(candidate_boards, k=COMMENTS_PER_USER):
            comment = Comment(
                author_id=user.id,
                board_id=board.id,
                content=rng.choice(COMMENT_TEMPLATES),
            )
            db.add(comment)
            comment_count += 1

    db.flush()
    return comment_count


def create_likes(db, users: list[User], boards: list[Board], rng: random.Random) -> int:
    like_count = 0

    for user in users:
        candidate_boards = [board for board in boards if board.author_id != user.id] or boards
        for board in rng.sample(candidate_boards, k=LIKES_PER_USER):
            db.add(BoardLike(user_id=user.id, board_id=board.id))
            like_count += 1

    db.flush()
    return like_count


def main() -> None:
    rng = random.Random(RANDOM_SEED)
    Base.metadata.create_all(bind=engine)
    db = session()

    try:
        reset_existing_mock_data(db)
        categories = get_or_create_categories(db)
        tags = get_or_create_tags(db)
        users = create_users(db)
        boards = create_boards(db, users, categories, tags, rng)
        comment_count = create_comments(db, users, boards, rng)
        like_count = create_likes(db, users, boards, rng)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print("Mock data inserted.")
    print(f"Accounts: {len(users)}")
    print(f"Boards: {len(boards)}")
    print(f"Comments: {comment_count}")
    print(f"Likes: {like_count}")
    print(f"Password: {TEST_PASSWORD}")
    for account in ACCOUNT_SPECS:
        print(
            f"- {account['email']} / {account['nickname']} / "
            f"{account['post_count']} boards"
        )


if __name__ == "__main__":
    main()
