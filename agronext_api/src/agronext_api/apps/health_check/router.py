from fastapi import APIRouter, status

from .exceptions import FailedHealthCheckException
from .schemas import HealthCheckResponse

router = APIRouter(prefix="/health_check", tags=["Health Check"])


@router.get(
    "/",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> dict:
    try:
        return {"status": "ok"}
    except Exception as e:
        raise FailedHealthCheckException(str(e)) from e
