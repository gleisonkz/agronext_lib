from ...exceptions.base import status, BaseHTTPException


class FailedHealthCheckException(BaseHTTPException):
    def __init__(self, message: str = "") -> None:
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.message = (
            f"Internal Server Error - {message}" if message else "Internal Server Error"
        )
        super().__init__(status_code=self.status_code, message=self.message)
