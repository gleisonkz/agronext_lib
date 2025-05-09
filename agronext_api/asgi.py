from agronext_api import create_router, create_api, run


## -- Thin factory to avoid eager instantiation -- ##
def dummy_api():
    router_a = create_router(prefix="/xpto", tags=["xpto"])

    @router_a.get("/hello")
    async def hello() -> dict[str, str]:
        """
        Hello world endpoint.
        """
        return {"message": "Hello, world!"}

    app = create_api(
        title="Dummy API",
        description="Dummy API for testing purposes",
        version="0.0.1",
        apps=[
            router_a,
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
