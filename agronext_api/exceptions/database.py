'''
TODO: Move to database module
'''

class BaseException(Exception):
    def __init__(self, message: str) -> None:
        self.message = f"Database: {message}"

    def __str__(self) -> str:
        return self.message


class Forbidden(BaseException):
    def __init__(self, message: str = None) -> None:
        self.message = "Forbidden" + f" - {message}" if message else ""
        super().__init__(self.message)


class Locked(BaseException):
    def __init__(self, message: str = None) -> None:
        self.message = "Locked" + f" - {message}" if message else ""
        super().__init__(self.message)


class Conflict(BaseException):
    def __init__(self, message: str = None) -> None:
        self.message = "Conflict" + f" - {message}" if message else ""
        super().__init__(self.message)


class Unauthorized(BaseException):
    def __init__(self, message: str = None) -> None:
        self.message = "Unauthorized" + f" - {message}" if message else ""
        super().__init__(self.message)


class DependencyError(BaseException):
    def __init__(self, message: str = None) -> None:
        self.message = "Dependency Error" + f" - {message}" if message else ""
        super().__init__(self.message)


class InternalServerError(BaseException):
    def __init__(self, message: str = None) -> None:
        self.message = "Internal Server Error" + f" - {message}" if message else ""
        super().__init__(self.message)


class BaseDatabaseException(Exception):
    def __init__(self, model: str, message: str) -> None:
        self.model = model
        self.message = message

    def __str__(self) -> str:
        return f"{self.model} - {self.message}"


class ResourceNotFound(BaseDatabaseException):
    def __init__(self, model: str) -> None:
        self.model = model
        self.message = "Resource not found"
        super().__init__(model, self.message)


class ResourceAlreadyExists(BaseDatabaseException):
    def __init__(self, model: str) -> None:
        self.model = model
        self.message = "Resource already exists"
        super().__init__(model, self.message)


class QueryError(BaseDatabaseException):
    def __init__(self, model: str, message: str) -> None:
        self.model = model
        self.message = message
        super().__init__(model, self.message)
