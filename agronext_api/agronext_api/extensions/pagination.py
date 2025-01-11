from fastapi import FastAPI
from fastapi_pagination import (
    add_pagination,
    paginate,  # noqa
)
from fastapi_pagination.utils import disable_installed_extensions_check


def init_pagination(app: FastAPI) -> None:
    add_pagination(app)
    disable_installed_extensions_check()
