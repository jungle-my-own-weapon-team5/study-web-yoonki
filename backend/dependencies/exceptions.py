from fastapi import HTTPException

from domain.exceptions import (
    BadRequestError,
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)


def to_http_exception(error: DomainError) -> HTTPException:
    if isinstance(error, BadRequestError):
        return HTTPException(status_code=400, detail=error.detail)

    if isinstance(error, UnauthorizedError):
        return HTTPException(status_code=401, detail=error.detail)

    if isinstance(error, ForbiddenError):
        return HTTPException(status_code=403, detail=error.detail)

    if isinstance(error, NotFoundError):
        return HTTPException(status_code=404, detail=error.detail)

    if isinstance(error, ConflictError):
        return HTTPException(status_code=409, detail=error.detail)

    return HTTPException(status_code=500, detail="Internal server error")
