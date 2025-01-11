from fastapi import HTTPException, status  # noqa


class BaseHTTPException(HTTPException):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(status_code=status_code, detail=message)

    def __str__(self) -> str:
        return f"{self.detail}"
