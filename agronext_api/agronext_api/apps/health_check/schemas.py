from ...schemas.base_model import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
