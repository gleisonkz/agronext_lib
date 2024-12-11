from fastapi import status
from .base import BaseHTTPException


class InvalidCredentialsError(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.message = f"Invalid Credentials Error - {message}" if message else "Invalid Credentials Error"
        super().__init__(status_code=self.status_code, message=self.message)


class AuthenticationError(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f"Authentication Error - {message}" if message else "Authentication Error"
        super().__init__(status_code=self.status_code, message=self.message)


class UnauthorizedError(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f"Unauthorized Error - {message}" if message else "Unauthorized Error"
        super().__init__(status_code=self.status_code, message=self.message)


class InternalServerError(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.message = f"Internal Server Error - {message}" if message else "Internal Server Error"
        super().__init__(status_code=self.status_code, message=self.message)


