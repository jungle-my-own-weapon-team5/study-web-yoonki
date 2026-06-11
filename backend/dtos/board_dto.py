from datetime import datetime
from pydantic import BaseModel

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

class BoardResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime | None = None

    # dict뿐 아니라 객체 attribute에서도 값을 읽어 response 모델을 만들 수 있게 함
    model_config = {
        "from_attributes": True
    }
