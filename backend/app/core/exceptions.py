from fastapi import HTTPException, status


class APIError(HTTPException):
    """Base API error with structured detail."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
    ) -> None:
        self.error_code = error_code or "GENERIC_ERROR"
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(APIError):
    def __init__(self, resource: str, resource_id: int | str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with id '{resource_id}' not found",
            error_code="NOT_FOUND",
        )


class ConflictError(APIError):
    def __init__(self, resource: str, field: str, value: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} with {field} '{value}' already exists",
            error_code="CONFLICT",
        )


class ValidationError(APIError):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )


class InternalError(APIError):
    def __init__(self, detail: str = "An internal error occurred") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="INTERNAL_ERROR",
        )
