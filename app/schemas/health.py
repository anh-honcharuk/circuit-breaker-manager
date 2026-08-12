from datetime import datetime

from pydantic import BaseModel

from app.db.models import CircuitState


class HealthResponse(BaseModel):
    service_id: int
    service_name: str
    status: str
    state: CircuitState
    response_time_ms: float | None = None
    checked_at: datetime