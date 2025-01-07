from fastapi import FastAPI

from .profiling import ProcessTimeMiddleware


def init_middlewares(app: FastAPI) -> None:
    app.add_middleware(ProcessTimeMiddleware)
