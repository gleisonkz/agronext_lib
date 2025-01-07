from fastapi import FastAPI

from .pagination import init_pagination


def init_extensions(app: FastAPI) -> None:
    init_pagination(app)
