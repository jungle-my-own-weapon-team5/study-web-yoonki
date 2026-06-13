from datetime import datetime
from pydantic import BaseModel, Field

'''
Pydantic은 원래 딕셔너리 값을 기대함.
그런데, Response모델은 클래스를 넘겨주니, model_config옵션으로 attributes에서도 읽으라고 해줘야함
'''

class BoardCreateRequest(BaseModel):
    title: str
    content: str
    category_id: int
    tags: list[str] | None = None

class BoardUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None
    tags: list[str] | None = None

class CategoryResponse(BaseModel):
    id: int
    title: str

    model_config = {
        "from_attributes": True
    }

class TagResponse(BaseModel):
    id: int
    title: str

    model_config = {
        "from_attributes": True
    }

class BoardResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    category_id: int
    category: CategoryResponse
    tags: list[TagResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None

    # dict뿐 아니라 객체 attribute에서도 값을 읽어 response 모델을 만들 수 있게 함
    model_config = {
        "from_attributes": True
    }

class BoardListResponse(BaseModel):
    items: list[BoardResponse]
    page: int
    size: int
    total: int

class BoardSummaryResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class BoardNeighborsResponse(BaseModel):
    previous: BoardSummaryResponse | None = None
    next: BoardSummaryResponse | None = None
