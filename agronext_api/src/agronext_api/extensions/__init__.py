from fastapi import FastAPI

from .pagination import init_pagination


def init_extensions(app: FastAPI, custom_extensions: list) -> None:
    init_pagination(app)

    if custom_extensions:
        raise NotImplementedError("Custom Extension is not implemented yet.")
