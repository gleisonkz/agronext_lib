from fastapi import status

from .base import BaseHTTPException


class Unauthorized(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        status_code = status.HTTP_401_UNAUTHORIZED
        message = f"Unauthorized - {message}" if message else "Unauthorized"
        super().__init__(status_code=status_code, message=message)


class Forbidden(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        status_code = status.HTTP_403_FORBIDDEN
        message = f"Forbidden - {message}" if message else "Forbidden"
        super().__init__(status_code=status_code, message=message)


class Locked(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        status_code = status.HTTP_423_LOCKED
        message = f"Locked - {message}" if message else "Locked"
        super().__init__(status_code=status_code, message=message)
