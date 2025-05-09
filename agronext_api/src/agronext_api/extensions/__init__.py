from fastapi import FastAPI

from .pagination import init_pagination


def init_extensions(app: FastAPI, custom_extensions: list) -> None:
    init_pagination(app)

    for extension in custom_extensions:
        raise NotImplementedError("Custom Extension is not implemented yet.")
