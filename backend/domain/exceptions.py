class DomainError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class BadRequestError(DomainError):
    pass


class UnauthorizedError(DomainError):
    pass


class ForbiddenError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass
