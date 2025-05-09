from fastapi.exceptions import (
    HTTPException,
    RequestValidationError,
    ResponseValidationError,
)  # noqa: F401


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(status_code=status_code, detail=message)

    def __str__(self) -> str:
        return f"{self.detail}"


class LifespanEventError(Exception):
    """Exception raised for errors in the lifespan event."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class StartupError(Exception):
    """Exception raised for errors during startup."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ShutdownError(Exception):
    """Exception raised for errors during shutdown."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
