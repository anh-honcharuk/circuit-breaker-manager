from datetime import datetime

from pydantic import BaseModel

from app.db.models import CircuitState


class CircuitBreakerResponse(BaseModel):
    service_id: int
    state: CircuitState
    changed_at: datetime
    message: str