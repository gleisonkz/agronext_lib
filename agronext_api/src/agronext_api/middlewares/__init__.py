from fastapi import FastAPI

from .profiling import ProcessTimeMiddleware


def init_middlewares(app: FastAPI, custom_middlewares: list) -> None:
    app.add_middleware(ProcessTimeMiddleware)

    for middleware in custom_middlewares:
        app.add_middleware(middleware)
