from ...exceptions.http import InternalServerError


class FailedHealthCheckException(InternalServerError):
    """Exception raised when the health check fails."""

    def __init__(self, message: str) -> None:
        super().__init__(f"HEALTH_CHECK_FAILED: {message}")
