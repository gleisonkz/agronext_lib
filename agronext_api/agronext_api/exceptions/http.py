from fastapi import status

from .base import BaseHTTPException


class BadRequest(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = f"Bad Request - {message}" if message else "Bad Request"
        super().__init__(status_code=self.status_code, message=self.message)


class NotFound(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.message = f"Not Found - {message}" if message else "Not Found"
        super().__init__(status_code=self.status_code, message=self.message)


class Conflict(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_409_CONFLICT
        self.message = f"Conflict - {message}" if message else "Conflict"
        super().__init__(status_code=self.status_code, message=self.message)


class UnavailableForLegalReasons(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
        self.message = f"Unavailable For Legal Reasons - {message}" if message else "Unavailable For Legal Reasons"
        super().__init__(status_code=self.status_code, message=self.message)


class InternalServerError(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = f"Internal Server Error - {message}" if message else "Internal Server Error"
        super().__init__(status_code=status_code, message=message)


class BadGateway(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_502_BAD_GATEWAY
        self.message = f"Bad Gateway - {message}" if message else "Bad Gateway"
        super().__init__(status_code=self.status_code, message=self.message)


class GatewayTimeout(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_504_GATEWAY_TIMEOUT
        self.message = f"Gateway Timeout - {message}" if message else "Gateway Timeout"
        super().__init__(status_code=self.status_code, message=self.message)


## Auth


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
