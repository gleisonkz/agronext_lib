from agronext_api import create_router, create_api, run
from agronext_api.exceptions import http
from agronext_api.integrations.teams import TeamsLogHandler
from agronext_api.logger import register_log_notification_handler, logging


## -- Thin factory to avoid eager instantiation -- ##
def dummy_api():
    router_a = create_router(prefix="/xpto", tags=["xpto"])

    register_log_notification_handler(
        "agronext_api.integrations.teams",
        TeamsLogHandler,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    @router_a.get("/hello")
    async def hello() -> dict[str, str]:
        """
        Hello world endpoint.
        """
        raise ZeroDivisionError("This is a test error for Teams notification")
        return {"message": "Hello, world!"}

    app = create_api(
        title="Dummy API",
        description="Dummy API for testing purposes",
        version="0.0.1",
        apps=[
            router_a,
        ],
        notification_handlers=[
            "agronext_api.integrations.teams",
        ],
    )
    return app


if __name__ == "__main__":
    run(
        api=dummy_api,
        factory=True,
        host="0.0.0.0",
        port=8000,
    )
